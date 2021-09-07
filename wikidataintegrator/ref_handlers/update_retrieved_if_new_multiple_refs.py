####
# custom ref handler
# If the newref is the same as the oldref except the retrieved date is `days` newer, overwrite
#                                                the retrieved date is NOT `days` newer, keep the old ref
# If the refs are different (in any other way), overwrite with new ref
#
####
from datetime import datetime


def update_retrieved_if_new_multiple_refs(olditem, newitem, days=180, retrieved_pid='P813'):
    """
    # modifies olditem in place
    # any ref that does not exactly match the new proposed reference (not including retrieved) is kept
    """

    def is_equal_not_retrieved(oldref, newref):
        """
        Return True if the oldref == newref, NOT including any "retrieved" statements

        :param oldref:
        :param newref:
        :return:
        """
        if len(oldref) != len(newref):
            return False
        oldref_minus_retrieved = [x for x in oldref if x.get_prop_nr() != retrieved_pid]
        newref_minus_retrieved = [x for x in newref if x.get_prop_nr() != retrieved_pid]
        if not all(x in oldref_minus_retrieved for x in newref_minus_retrieved):
            return False
        oldref_retrieved = [x for x in oldref if x.get_prop_nr() == retrieved_pid]
        newref_retrieved = [x for x in newref if x.get_prop_nr() == retrieved_pid]
        if (len(newref_retrieved) != len(oldref_retrieved)):
            return False
        return True

    def ref_overwrite(oldref, newref, days):
        """
        If the newref is the same as the oldref except the retrieved date is `days` newer, return True
                                                       the retrieved date is NOT `days` newer, return False
        the refs are different, return True
        """
        if len(oldref) != len(newref):
            return True
        oldref_minus_retrieved = [x for x in oldref if x.get_prop_nr() != retrieved_pid]
        newref_minus_retrieved = [x for x in newref if x.get_prop_nr() != retrieved_pid]
        if not all(x in oldref_minus_retrieved for x in newref_minus_retrieved):
            return True
        oldref_retrieved = [x for x in oldref if x.get_prop_nr() == retrieved_pid]
        newref_retrieved = [x for x in newref if x.get_prop_nr() == retrieved_pid]
        if (len(newref_retrieved) != len(oldref_retrieved)) or not (
                        len(newref_retrieved) == len(oldref_retrieved) == 1):
            return True
        datefmt = '+%Y-%m-%dT%H:%M:%SZ'
        retold = list([datetime.strptime(r.get_value()[0], datefmt) for r in oldref if r.get_prop_nr() == retrieved_pid])[0]
        retnew = list([datetime.strptime(r.get_value()[0], datefmt) for r in newref if r.get_prop_nr() == retrieved_pid])[0]
        return (retnew - retold).days >= days

    newrefs = newitem.references
    oldrefs = olditem.references

    found_mate = [False] * len(newrefs)
    for new_n, newref in enumerate(newrefs):
        for old_n, oldref in enumerate(oldrefs):
            if is_equal_not_retrieved(oldref, newref):
                found_mate[new_n] = True
                if ref_overwrite(oldref, newref, days):
                    oldrefs[old_n] = newref
    for f_idx, f in enumerate(found_mate):
        if not f:
            oldrefs.append(newrefs[f_idx])
