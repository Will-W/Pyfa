# shipBonusForceAuxiliaryRole1CPUBonus
#
# Used by:
# Ships from group: Force Auxiliary (4 of 4)
type = "passive"


def handler(fit, src, context):
    fit.modules.filteredItemBoost(lambda mod: mod.item.requiresSkill("Leadership"), "cpu",
                                  src.getModifiedItemAttr("shipBonusRole1"))
