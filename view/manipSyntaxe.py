def stringToRelationObject(s):#Takes a string (ie: "tigre r_agent-1 chasser")and returns an object as follows: {"n1":"tigre","r":"r_agent-1","n2":"chasser"}
	parsed = s.split(" ")
	if len(parsed)!=3:
		return None
	else:
		return {"nt":parsed[0],"r":parsed[1],"n2":parsed[2]}


def stringToNodesForRelation(s):
	parsed = s.split(" ")
	if len(parsed)!=4:
		return None
	else:
		return {"n1":parsed[1],"n2":parsed[3]}
