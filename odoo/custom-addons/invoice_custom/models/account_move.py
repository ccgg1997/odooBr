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
            if product.product_template_attribute_value_ids:
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
                    "default_code": self.get_base_default_code(product.default_code),
                    "variants": [],
                    "qty": 0.0,
                    "unit_price": 0.0,
                    "subtotal": 0.0,
                    "uom_id": product.uom_id,
                    "tax_ids": line.tax_ids,
                    "total_qty_for_avg": 0.0,  # Para calcular precio promedio
                }

            # Agregar información de esta variante
            if variant_name:
                groups[key]["variants"].append(f"{int(line.quantity)} {variant_name}")
            else:
                groups[key]["variants"].append(f"{int(line.quantity)}")

            groups[key]["qty"] += line.quantity
            groups[key]["subtotal"] += line.price_subtotal
            # Recalcular precio unitario promedio ponderado
            if groups[key]["qty"] > 0:
                groups[key]["unit_price"] = groups[key]["subtotal"] / groups[key]["qty"]

        # Procesar grupos finales
        result = []
        for group_data in groups.values():
            # Limpiar campo auxiliar
            group_data.pop("total_qty_for_avg", None)
            
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
                    "default_code": group_data["default_code"]
                },
            )

            result.append(group_data)

        return result

    @staticmethod
    def get_base_default_code(default_code):
        if default_code and '-' in default_code:
            return default_code.split('-')[0]
        return default_code or ""
    