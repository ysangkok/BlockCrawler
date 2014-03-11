#!/usr/bin/env python3
import json
import bc_daemon
import bc_layout

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
			<form action="" method="post">
			<input type="text" name="block_height" size="40">
			<input type="submit" name="submit" value="Jump To Block">
			</form>
		</div>
	
		<div class="menu_item">
			<span class="menu_desc">Enter A Block Hash</span><br>
			<form action="" method="post">
			<input type="text" name="block_hash" size="40">
			<input type="submit" name="submit" value="Jump To Block">
			</form>
		</div>
	
		<div class="menu_item">
			<span class="menu_desc">Enter A Transaction ID</span><br>
			<form action="" method="post">
			<input type="text" name="transaction" size="40">
			<input type="submit" name="submit" value="Jump To TX">
			</form>
		</div>
		</div>
		<div style='clear:both'></div>"""
	
	yield from bc_layout.site_footer()

if __name__ == "__main__":
	import cgi, sys, os
	import cgitb; cgitb.enable()
	if "PATH_INFO" in os.environ and "block_crawler.css" in os.environ["PATH_INFO"]:
		sys.stdout.buffer.write(b"Content-Type: text/css\n\n")
		with open("/var/www/cgi-bin/block/block_crawler.css","rb") as f:
			sys.stdout.buffer.write(f.read())
		sys.stdout.buffer.flush()
	else:
		print("Content-Type: text/html")
		print("")
		for i in main(cgi.FieldStorage()):
			print(i,end="")
