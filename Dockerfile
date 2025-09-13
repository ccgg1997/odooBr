FROM odoo:18.0
USER root

COPY --chown=odoo:odoo custom-addons/ /mnt/extra-addons/
COPY --chown=odoo:odoo odoo/config/odoo.conf /etc/odoo/odoo.conf
ENV ADDONS_PATH="/usr/lib/python3/dist-packages/odoo/addons,/mnt/extra-addons"
EXPOSE 8069 8072
USER odoo
CMD ["odoo"]