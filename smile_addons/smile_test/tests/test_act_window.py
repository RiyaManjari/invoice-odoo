# -*- coding: utf-8 -*-
# (C) 2018 Smile (<http://www.smile.fr>)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import datetime
from dateutil.relativedelta import relativedelta
import time

from odoo.tests.common import TransactionCase


class TestActWindow(TransactionCase):

    def test_act_window(self):
        """ I tests all search and first reads for all act_windows.
        """
        errors = []
        # Only tests act_window from menus: others might require active_ids
        menu_infos = self.env['ir.ui.menu'].search_read([], ['action'])
        user_context = self.env['res.users'].context_get()
        actions = [info['action'].split(',')
                   for info in menu_infos if info['action']]
        act_window_ids = list(set([int(res_id)
                                   for model, res_id in actions
                                   if model == 'ir.actions.act_window']))
        # context built as in webclient
        user_context.update({
            'active_model': '',
            'active_id': False,
            'active_ids': [],
            'uid': self.env.user.id,
            'user': self.env.user,
            'time': time,
            'datetime': datetime,
            'relativedelta': relativedelta,
            'current_date': time.strftime('%Y-%m-%d'),
        })
        act_windows = self.env['ir.actions.act_window'].browse(act_window_ids)
        for act_window in act_windows:
            model = act_window.res_model
            buf_context = user_context.copy()
            try:
                with self.env.cr.savepoint():
                    test_context = eval(
                        act_window.context and act_window.context.strip() or
                        '{}', buf_context) or buf_context
                    test_domain = eval(
                        act_window.domain and act_window.domain.strip() or
                        '[]', buf_context) or []
                    test_limit = int(act_window.limit) if act_window.limit \
                        else None
                    self.env[model].with_context(**test_context).search_read(
                        test_domain, offset=0, limit=test_limit)
            except Exception as e:
                err_info = (act_window.name, act_window.res_model,
                            act_window.domain, act_window.limit,
                            act_window.context, repr(e))
                errors.append(err_info)
        err_details = "\n".join(
            ["(%s, %s, %s, %s, %s): %s" % error for error in errors])
        error_msg = "Error in search/read for act_window/model " \
            "and error:\n%s" % err_details
        self.assertEquals(len(errors), 0, error_msg)
