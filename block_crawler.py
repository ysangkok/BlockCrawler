#!/usr/bin/env python3
import json
import bc_daemon
import bc_layout
import sqlite3

def main(REQUEST):
	# If a block hash was provided the block detail is shown
	if "block_hash" in REQUEST:
		yield from bc_layout.site_header("Block Detail Page")
		yield from bc_layout.block_detail(REQUEST["block_hash"].value, True)
	
	# If a block height is provided the block detail is shown
	elif "block_height" in REQUEST:
		yield from bc_layout.site_header("Block Detail Page")
		yield from bc_layout.block_detail(REQUEST["block_height"].value)
	# If a TXid was provided the TX Detail is shown
	elif "transaction" in REQUEST:
		yield from bc_layout.site_header("Transaction Detail Page")
		yield from bc_layout.tx_detail(REQUEST["transaction"].value)
	elif "address" in REQUEST:
		c = sqlite3.connect('riecoin_tools/stats/out/db')
		res = c.execute('select * from balances where address=?', (REQUEST["address"].value,))
		row = res.fetchone()
		if row:
			yield "address {}<br>with balance <b>{}</b><br>was last used<br><b>{} days ago</b>".format(*row)
		else:
			yield "address unknown (maybe it has a balance less than 1?)"
		c.close()
		return
	
	# If there were no request parameters the menu is shown
	else:
		yield from bc_layout.site_header ("Block Crawler Home Page")
		yield "	<div id=\"node_info\">"
		network_info = bc_daemon.getinfo()
		yield "		<p class=\"node_detail\">"
		yield "			<span class=\"node_desc\">Block Count:</span><br>"
		yield "			"+bc_layout.blockheight_link(network_info["blocks"])
		yield "		</p>"
	
		yield "		<p class=\"node_detail\">"
		yield "			<span class=\"node_desc\">Difficulty:</span><br>"
		yield "			"+str(network_info["difficulty"])
		yield "		</p>"
	
		yield "		<p class=\"node_detail\">"
		yield "			<span class=\"node_desc\">Connections:</span><br>"
		yield "			"+str(network_info["connections"])
		yield "		</p>"
	
		net_speed = bc_daemon.getnetworkhashps()
		if net_speed != "":
			yield "		<p class=\"node_detail\">"
			yield "			<span class=\"node_desc\">Network H/s:</span><br>"
			yield "			"+str(net_speed)
			yield "		</p>"
		yield "</div>"
	
		yield """<div id="site_menu">
		<div class="menu_item">
			<span class="menu_desc">Enter a Block Index / Height</span><br>
			<form action="" method="get">
			<input type="text" name="block_height" size="40">
			<input type="submit" name="submit" value="Show Block">
			</form>
		</div>
	
		<div class="menu_item">
			<span class="menu_desc">Enter a Block Hash</span><br>
			<form action="" method="get">
			<input type="text" name="block_hash" size="40">
			<input type="submit" name="submit" value="Show Block">
			</form>
		</div>
	
		<div class="menu_item">
			<span class="menu_desc">Enter a Transaction ID</span><br>
			<form action="" method="get">
			<input type="text" name="transaction" size="40">
			<input type="submit" name="submit" value="Show TX">
			</form>
		</div>

		<div class="menu_item">
			<span class="menu_desc">Enter an Address</span><br>
			<form action="" method="get" target="addrresult">
			<input type="text" name="address" size="40">
			<input type="submit" name="submit" value="Show Balance">
			</form>
			<iframe src="about:blank" name="addrresult"></iframe>
		</div>

		</div>
		<div style='clear:both'></div>"""
	
	yield from bc_layout.site_footer()

if __name__ == "__main__":
	import cgi, sys, os, os.path
	import cgitb; cgitb.enable()

	if ("QUERY_STRING" not in os.environ or len(os.environ["QUERY_STRING"]) < 2) and ("PATH_INFO" not in os.environ or len(os.environ["PATH_INFO"]) < 2):
		sys.stdout.buffer.write(b"Cache-Control: no-store\n")
		sys.stdout.buffer.flush()

	if "PATH_INFO" in os.environ and "block_crawler.css" in os.environ["PATH_INFO"]:
		sys.stdout.buffer.write(b"Content-Type: text/css\n\n")
		with open(os.path.dirname(os.path.abspath(__file__)) + "/block_crawler.css","rb") as f:
			sys.stdout.buffer.write(f.read())
		sys.stdout.buffer.flush()
	else:
		print("Content-Type: text/html")
		print("")
		for i in main(cgi.FieldStorage()):
			print(i,end="")
