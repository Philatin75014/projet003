try:
    from . import prestataire_reference
    from . import comite_reference
    from . import paramcanalcampagneoffre
    from . import refresh
except ImportError:
    # Ignore les erreurs d'import lorsque vous êtes en dehors d'Odoo
    pass
