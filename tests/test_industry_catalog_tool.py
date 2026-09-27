import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).resolve().parents[1] / "tools" / "industry_catalog.py"
SPEC = importlib.util.spec_from_file_location("industry_catalog", MODULE_PATH)
industry_catalog = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(industry_catalog)


class IndustryCatalogTest(unittest.TestCase):
    def _write_manifest(self, root: Path, slug: str, payload: str) -> None:
        module = root / slug
        module.mkdir(parents=True)
        (module / "__manifest__.py").write_text(payload, encoding="utf-8")

    def test_public_catalog_only_includes_application_modules(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write_manifest(
                root,
                "hotel",
                "{'name':'Hotel','category':'Hospitality','application':True,"
                "'depends':['website','base'],'images':['images/main.png'],"
                "'url':'https://www.odoo.com/trial?industry&selected_app=hotel',"
                "'website':'https://www.odoo.com/industries/hotel'}",
            )
            self._write_manifest(
                root,
                "booking_engine",
                "{'name':'Booking Engine','application':False,'depends':['base']}",
            )

            catalog = industry_catalog.build_catalog(root)

            self.assertEqual([row["slug"] for row in catalog], ["hotel"])
            self.assertEqual(catalog[0]["canonical_path"], "/segmentos/hotel")
            self.assertEqual(catalog[0]["trial_path"], "/go/industry/hotel")
            self.assertEqual(catalog[0]["depends"], ["base", "website"])
            self.assertTrue(catalog[0]["source_url"].startswith("https://www.odoo.com/"))

    def test_include_support_is_deterministic(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write_manifest(root, "zeta", "{'name':'Zeta','application':True}")
            self._write_manifest(root, "alpha", "{'name':'Alpha','application':False}")

            catalog = industry_catalog.build_catalog(root, include_support=True)

            self.assertEqual([row["name"] for row in catalog], ["Alpha", "Zeta"])


if __name__ == "__main__":
    unittest.main()
