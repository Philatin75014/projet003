from odoo import models, fields, api
#from odoo import models, fields, api
#from .utils.datasource import get_param_canal_campagne_offre_data  # Import depuis le sous-répertoire
#from .utils.datasource import get_source_mpa_data  # Import depuis le sous-répertoire
#from .utils.datasource import get_comites_data  
    

class Refresh(models.TransientModel):
    _name = 'refresh'
    _description = 'pour rafraîchir les données'

    # Définir les champs dont vous avez besoin dans le wizard
    #confirmation = fields.Boolean(string="Confirmer le rafraîchissement", required=True)

    def action_refresh_data(self):
        # Logique pour rafraîchir les données
        self.env['param.canal.campagne.offre'].manual_reload_data()
      #  return {'type': 'ir.actions.act_window_close'}  # Ferme le wizard
        return {
        'type': 'ir.actions.act_window',
        'name': 'Param Canal Campagne Offres',
         'res_model': 'param.canal.campagne.offre',
         'view_mode': 'tree',
         'target': 'current',  # Cela peut être 'new' si vous souhaitez ouvrir dans une nouvelle fenêtre
          }

      