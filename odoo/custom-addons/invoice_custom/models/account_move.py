from odoo import models


class AccountMove(models.Model):
    _inherit = "account.move"

    def _get_grouped_lines(self):
        self.ensure_one()
        groups = {}

        for line in self.invoice_line_ids.filtered(lambda l: l.product_id):
            product = line.product_id

            # Usar el template ID para agrupar productos con variantes
            key = product.product_tmpl_id.id

            # Obtener el nombre de la variante específica
            variant_attrs = []
            if hasattr(product, "product_template_attribute_value_ids"):
                for attr_value in product.product_template_attribute_value_ids:
                    variant_attrs.append(attr_value.name)

            # Si no hay atributos, intentar extraer la variante del nombre
            if not variant_attrs and product.name != product.product_tmpl_id.name:
                variant_name = product.name.replace(
                    product.product_tmpl_id.name, ""
                ).strip("() ")
                if variant_name:
                    variant_attrs.append(variant_name)

            variant_name = ", ".join(variant_attrs)

            if key not in groups:
                groups[key] = {
                    "product": product.product_tmpl_id,
                    "product_name": product.product_tmpl_id.name,
                    "variants": [],
                    "qty": 0.0,
                    "price_unit": line.price_unit,
                    "subtotal": 0.0,
                    "uom_id": product.uom_id,
                    "tax_ids": line.tax_ids,  # Guardar impuestos de la primera línea
                }

            # Agregar información de esta variante
            if variant_name:
                groups[key]["variants"].append(f"{int(line.quantity)} {variant_name}")
            else:
                groups[key]["variants"].append(f"{int(line.quantity)}")

            groups[key]["qty"] += line.quantity
            groups[key]["subtotal"] += line.price_subtotal

        # Procesar grupos finales
        result = []
        for group_data in groups.values():
            # Unir las variantes
            group_data["variants"] = ", ".join(group_data["variants"])

            # Crear objeto compatible con la plantilla
            group_data["product"] = type(
                "obj",
                (object,),
                {
                    "display_name": group_data["product_name"],
                    "name": group_data["product_name"],
                    "uom_id": group_data["uom_id"],
                },
            )

            result.append(group_data)

        return result
