# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, tools, _
from odoo.exceptions import UserError,ValidationError
from odoo.tools import float_is_zero, pycompat
from odoo.addons import decimal_precision as dp
from odoo.osv import expression
from datetime import date,datetime
import logging
_logger = logging.getLogger(__name__)

class SaleBlanketOrder(models.Model):
    _inherit = 'sale.blanket.order'


    @api.one
    @api.depends('muebles_especiales')
    def _get_muebles_especiales(self):
        if not self.env.user.has_group('re_sale_security.group_reno_technical_user'):
            self.muebles_readonly=False
        else:
            if self.state=='draft':
                self.muebles_readonly=True
            else:
                self.muebles_readonly=False


    muebles_readonly = fields.Boolean(compute='_get_muebles_especiales', string='Muebles Readonly', default=True)
    date_send_factory = fields.Date('Fecha Enviado a fabrica', help='Fecha de Enviado a fabrica (Acuerdos Normales)', track_visibility='onchange')
    date_order_def = fields.Date('Fecha Pedido definitivo', help='Fecha de pedido definitivo (Acuerdos a Futuro)', track_visibility='onchange')
    state = fields.Selection(track_visibility='onchange')
    condition_id = fields.Many2one(track_visibility='onchange')
    additional_discount = fields.Float(track_visibility='onchange')
    muebles_especiales = fields.Boolean(track_visibility='onchange')
    blanket_origin_id = fields.Many2one(track_visibility='onchange')
    acuerdo_futuro = fields.Boolean(track_visibility='onchange')
    claim = fields.Boolean(track_visibility='onchange')
    link_folder_16 = fields.Char(track_visibility='onchange')
    transport_id = fields.Many2one(track_visibility='onchange')
    advance = fields.Float('Advance', default='0.0')
    exchange = fields.Float('Exchange', default='0.0')
    upon_delivery = fields.Float('Upon Delivery', default='0.0')
    against_certification = fields.Float('Against Certification', default='0.0')
    repair_fund = fields.Float('Repair Fund', default='0.0')
    surety_financial_advanceund = fields.Float('Surety Policy Financial Advance', default='0.0')
    surety_repair_fund = fields.Float('Surety Policy Repair Fund.', default='0.0')
    note = fields.Text('Notes')
    proyect_id = fields.Many2one('account.project', string='Project')
    street = fields.Char('Street')
    city = fields.Char('City')
    state_id = fields.Many2one('res.country.state', string='State')
    operating_id = fields.Many2one('operating.unit', string='Operating')

    @api.multi
    def action_set_in_process(self):
        self.date_send_factory = datetime.now().strftime('%Y-%m-%d')
        if self.invoice_to and self.invoice_to=='manual':
            if not self.advance:
                raise ValidationError(_('The field Advanve is null'))
            if not self.exchange:
                raise ValidationError(_('The field exchange is null'))
            if not self.upon_delivery:
                raise ValidationError(_('The field upon_delivery is null'))
            if not self.against_certification:
                raise ValidationError(_('The field against_certification is null'))
            total = self.advance + self.exchange + self.upon_delivery + self.against_certification
            if total != self.total_amount:
                raise ValidationError(_('The payment terms do not match the value of the agreement'))
        res = super(SaleBlanketOrder, self).action_set_in_process()
        return res


    @api.multi
    def action_sent_to_manufacturing(self):
        self.date_order_def = datetime.now().strftime('%Y-%m-%d')
        res = super(SaleBlanketOrder, self).action_sent_to_manufacturing()
        return res


    @api.onchange('additional_discount')
    def onchange_additional_discount(self):
        if self.env.user.has_group('re_sale_security.group_re_administrativo') or self.env.user.has_group('re_sale_security.group_re_posventa') or self.env.user.has_group('re_sale_security.group_re_titular') or self.env.user.has_group('re_sale_security.group_re_vendedor'):
            if self.additional_discount not in (0, 10, 20, 30):
                raise ValidationError(_('Usted es un usuario de las Franquicias, solo tiene las siguientes opciones 0, 10, 20 y 30'))


    @api.model
    def create(self, vals):
        if vals.get('additional_discount', False):
            if self.env.user.has_group('re_sale_security.group_re_administrativo') or self.env.user.has_group('re_sale_security.group_re_posventa') or self.env.user.has_group('re_sale_security.group_re_titular') or self.env.user.has_group('re_sale_security.group_re_vendedor'):
                if vals.get('additional_discount', False) not in (0, 10, 20, 30):
                    raise ValidationError(_('Usted es un usuario de las Franquicias, solo tiene las siguientes opciones 0, 10, 20 y 30'))
        return super(SaleBlanketOrder, self).create(vals)


    @api.multi
    def write(self, vals):
        if vals.get('additional_discount', False):
            if self.env.user.has_group('re_sale_security.group_re_administrativo') or self.env.user.has_group('re_sale_security.group_re_posventa') or self.env.user.has_group('re_sale_security.group_re_titular') or self.env.user.has_group('re_sale_security.group_re_vendedor'):
                if vals.get('additional_discount', False) not in (0, 10, 20, 30):
                    raise ValidationError(_('Usted es un usuario de las Franquicias, solo tiene las siguientes opciones 0, 10, 20 y 30'))
        if vals.get('advance', False) or vals.get('exchange', False) or vals.get('upon_delivery', False) or vals.get('against_certification', False):
            total = vals.get('advance', self.advance) +  vals.get('exchange', self.exchange) + vals.get('upon_delivery', self.upon_delivery) + vals.get('against_certification', self.against_certification)
            if total != self.total_amount:
                raise ValidationError(_('The payment terms do not match the value of the agreement'))
        return super(SaleBlanketOrder, self).write(vals)
