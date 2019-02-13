BEGIN {
	#print "BEGIN"
	FS=":"
	uid = 5000
	home = "/afs/ee.cooper.edu/user"
}

NR==1 {
	uid = $1
	#print "Start UID from " uid
}

NR!=1 { 
	OFS=":"
	sh = match($4,/[^ ]/) ? $4 : "/bin/bash"
	fl = substr($1,1,1)
	print $1,"x",uid++,"2001",$2" "$3,home"/"fl"/"$1,sh
}

END {
	#print "END"
}
