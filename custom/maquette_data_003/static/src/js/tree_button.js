odoo.define('Maquette003.tree_button', function (require) {
    "use strict";

    var ListView = require('web.ListView');
    console.log("Tree Button JS Chargé !");

    ListView.include({
        render_buttons: function ($node) {
            this._super($node);
            if (this.$buttons) {
                var button = $('<button/>', {
                    text: 'Rafraîchir',
                    class: 'btn btn-primary',
                    click: function () {
                        console.log('Bouton Rafraîchir cliqué');
                    }
                });
                this.$buttons.append(button);
            }
        }
    });
});
