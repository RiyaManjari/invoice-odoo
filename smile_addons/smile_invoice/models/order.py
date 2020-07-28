from odoo import fields, models
from odoo.exceptions import UserError


class Order(models.Model):
    _inherit = 'sale.order'

    validator_id = fields.Many2one('res.users', 'validators', default=lambda self: self.env.user)

    def action_confirm(self):
        if self.env.user.validation_threshold < self.amount_total:
            raise UserError("Sorry You don't have right to confirm this order")
        return super(Order, self).action_confirm()
