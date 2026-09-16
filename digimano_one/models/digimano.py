from odoo import api, fields, models, _
from odoo.exceptions import UserError


class DigimanoPatient(models.Model):
    _name = "digimano.patient"
    _description = "Digimano Patient"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "name"

    name = fields.Char(string="Primeiro nome", required=True, tracking=True)
    age = fields.Integer(string="Idade", required=True, tracking=True)
    active = fields.Boolean(default=True)
    shift_ids = fields.One2many("digimano.shift", "patient_id", string="Turnos")

    @api.constrains("age")
    def _check_age(self):
        for record in self:
            if record.age < 0 or record.age > 130:
                raise UserError(_("Informe uma idade válida entre 0 e 130 anos."))


class DigimanoShift(models.Model):
    _name = "digimano.shift"
    _description = "Digimano Care Shift"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _order = "start_at desc, id desc"

    patient_id = fields.Many2one(
        "digimano.patient", string="Paciente", required=True, ondelete="restrict", tracking=True
    )
    responsible_user_id = fields.Many2one(
        "res.users", string="Responsável atual", required=True, default=lambda self: self.env.user,
        tracking=True,
    )
    responsible_role = fields.Char(string="Função", required=True, tracking=True)
    incoming_user_id = fields.Many2one("res.users", string="Próximo responsável", tracking=True)
    start_at = fields.Datetime(string="Início", tracking=True)
    handoff_at = fields.Datetime(string="Entrega", tracking=True)
    accepted_at = fields.Datetime(string="Recebido em", tracking=True)
    initial_status = fields.Selection(
        [("stable", "Estável"), ("attention", "Atenção"), ("critical", "Crítico")],
        string="Avaliação inicial",
        tracking=True,
    )
    initial_note = fields.Char(string="Nota inicial")
    state = fields.Selection(
        [
            ("draft", "Rascunho"),
            ("active", "Em cuidado"),
            ("handoff", "Aguardando recebimento"),
            ("closed", "Entregue"),
        ],
        default="draft",
        required=True,
        tracking=True,
    )
    entry_ids = fields.One2many("digimano.care.entry", "shift_id", string="Registros")
    handoff_summary = fields.Text(string="Resumo da entrega", readonly=True, tracking=True)

    def action_start(self):
        for record in self:
            if record.state != "draft":
                continue
            record.write({"state": "active", "start_at": fields.Datetime.now()})
            record.message_post(body=_("Cuidado assumido por %s.") % record.responsible_user_id.display_name)

    def _build_handoff_summary(self):
        self.ensure_one()
        entries = self.entry_ids.sorted(lambda e: (e.occurred_at or fields.Datetime.now(), e.id))
        if not entries:
            return _("Sem registros durante este turno.")
        lines = []
        labels = dict(self.env["digimano.care.entry"]._fields["event_type"].selection)
        for entry in entries:
            when = fields.Datetime.to_string(entry.occurred_at) if entry.occurred_at else "-"
            value = entry.value_label or entry.note or _("registrado")
            lines.append(f"{when} | {labels.get(entry.event_type, entry.event_type)} | {value}")
        return "\n".join(lines)

    def action_prepare_handoff(self):
        for record in self:
            if record.state != "active":
                raise UserError(_("O turno precisa estar em cuidado para ser entregue."))
            if not record.incoming_user_id:
                raise UserError(_("Defina o próximo responsável antes da entrega."))
            summary = record._build_handoff_summary()
            record.write({
                "state": "handoff",
                "handoff_at": fields.Datetime.now(),
                "handoff_summary": summary,
            })
            record.message_post(body=_("Turno preparado para entrega a %s.\n\n%s") % (
                record.incoming_user_id.display_name, summary
            ))

    def action_accept_handoff(self):
        for record in self:
            if record.state != "handoff":
                raise UserError(_("Este turno não está aguardando recebimento."))
            previous = record.responsible_user_id
            incoming = record.incoming_user_id
            record.write({"state": "closed", "accepted_at": fields.Datetime.now()})
            record.message_post(body=_("Entrega confirmada por %s. Responsabilidade anterior: %s.") % (
                incoming.display_name, previous.display_name
            ))
            self.create({
                "patient_id": record.patient_id.id,
                "responsible_user_id": incoming.id,
                "responsible_role": record.responsible_role,
                "initial_status": record.initial_status,
                "state": "active",
                "start_at": fields.Datetime.now(),
            }).message_post(body=_("Novo ciclo de cuidado iniciado a partir da entrega anterior."))


class DigimanoCareEntry(models.Model):
    _name = "digimano.care.entry"
    _description = "Digimano Care Entry"
    _order = "occurred_at desc, id desc"

    shift_id = fields.Many2one(
        "digimano.shift", string="Turno", required=True, ondelete="cascade", index=True
    )
    patient_id = fields.Many2one(related="shift_id.patient_id", store=True, index=True)
    event_type = fields.Selection(
        [
            ("medication", "Medicamentos"),
            ("food", "Alimentação"),
            ("hydration", "Hidratação"),
            ("mood", "Humor"),
            ("general_state", "Estado geral"),
            ("incident", "Intercorrência"),
            ("observation", "Observação"),
        ],
        string="Tipo",
        required=True,
        index=True,
    )
    value_label = fields.Char(string="Resposta rápida")
    note = fields.Char(string="Observação curta")
    occurred_at = fields.Datetime(string="Data e hora", required=True, default=fields.Datetime.now, index=True)
    author_id = fields.Many2one(
        "res.users", string="Registrado por", required=True, default=lambda self: self.env.user,
        readonly=True,
    )

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        labels = dict(self._fields["event_type"].selection)
        for record in records:
            detail = record.value_label or record.note or _("registrado")
            record.shift_id.message_post(
                body=_("%s: %s (%s)") % (
                    labels.get(record.event_type, record.event_type),
                    detail,
                    record.author_id.display_name,
                )
            )
        return records
