base=""
pids=$(ps aux | grep 'chrome/chrome --type=renderer' | awk '{print $2}')
for p in $pids; do
	bases=$(pmap $p | grep '131072K' | awk '{print $1}')
	if [ ! -z "$bases" ]; then
		pid=$p
		break;
	fi
done
# find right allocated buffer if no gc yet
for c in $bases; do
	if [ -z "${allocated[c]}" ]; then
		allocated+=(["$c"]=1) # add element to avoid repeat
		base="0x$c"
		break;
	fi
done
if [ -z "$base" ]; then
	echo "[!] Error"
	exit 1
fi
echo "PID: $pid"
echo "Virtual base: $base"
