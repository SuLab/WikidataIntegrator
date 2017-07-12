from datetime import datetime
import copy
####
# Example custom ref handler
# Always replaces all old refs with new refs
####

def strict_overwrite(olditem, newitem):
    # modifies olditem in place!!!
    olditem.references = newitem.references