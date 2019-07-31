####
# custom ref handler
# If the newref is the same as the oldref except the retrieved date is `days` newer, overwrite
#                                                the retrieved date is NOT `days` newer, keep the old ref
# If the refs are different (in any other way), overwrite with new ref
#
# Only handles cases where olditem and newitem each have one reference. Otherwise, defaults to overwrite
####
from datetime import datetime
import copy

def update_retrieved_if_new(olditem, newitem, days=180, retrieved_pid='P813'):
    """
    # modifies olditem in place
    """
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
    if not (len(newrefs) == len(oldrefs) == 1):
        #print("overwriting refs, not 1")
        olditem.references = copy.deepcopy(newitem.references)
        return None
    overwrite = ref_overwrite(oldrefs[0], newrefs[0], days)
    if overwrite:
        print("updating ref")
        olditem.references = newrefs
    else:
        print("don't change")
        pass