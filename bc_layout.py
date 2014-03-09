import bc_daemon
import cgi
import textwrap
import datetime
import time
import json
from riecoin_tools.check_proof_of_work import get_primes_from_block

def site_header(title, auth_list=""):
		yield """<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN" "http://www.w3.org/TR/html4/loose.dtd">
		<head>
			<title>{title}</title>
			<link rel="stylesheet" type="text/css" href="block_crawler.css">
		</head>
		<body>
			<div id="site_head">
				<div id="site_head_logo">
					<h1><a href="." title="Home Page">
						Riecoin Block Crawler
					</a></h1>
				</div>
			</div>
			<div id="page_wrap">
		""".format(thisscript=".", title=title)

def site_footer():
	#	The page_wrap div is opened in the last line of the site_header function.
	yield """
			</div>
			<div id="donor_box">
				Donations: RTvFbTNfhurjiLPzZia1djJ7sUWVA6EtEe
			</div>
		</body>
		</html>
	"""

def strtoout(s):
	return datetime.datetime.fromtimestamp(int(s), tz=datetime.timezone.utc).isoformat()

def block_detail(block_id, hash=False):
		if hash:
			raw_block = bc_daemon.getblock (block_id)
		else:
			block_hash = bc_daemon.getblockhash (int(block_id))
			raw_block = bc_daemon.getblock(block_hash)

		yield """
			<div class="block_banner">
				<div class="blockbanner_left">
					Block Height: """+str(raw_block["height"])+"""
				</div>


				<div class="blockbanner_right">
					Block Time: """
		yield strtoout(raw_block["time"])
		yield """
				</div>
			</div>
			<div class="blockdetail">
				<div class="blockdetail_detail">
					<div class="blockdetail_header">Block Version</div>
					<div class="blockdetail_content">
						{version}
					</div>
				</div>
				<div class="blockdetail_detail">
					<div class="blockdetail_header">Block Size</div>
					<div class="blockdetail_content">
						{size}
					</div>
				</div>
				<div class="blockdetail_detail">
					<div class="blockdetail_header"># of Confirmations</div>
					<div class="blockdetail_content">
						{confirmations}
					</div>
				</div>
				<div class="blockdetail_detail">
					<div class="blockdetail_header">Block Bits</div>
					<div class="blockdetail_content">
						{bits}
					</div>
				</div>
				<div class="blockdetail_detail">
					<div class="blockdetail_header">Block Difficulty</div>
					<div class="blockdetail_content">
						{difficulty}
					</div>
				</div>
			</div>
		""".format(**raw_block)

		yield from detail_display ("Block Offset", raw_block["nOffset"])

		if raw_block["height"] != 0:
			for offset, prime in get_primes_from_block(raw_block):
				yield from detail_display("Prime n+{}".format(offset), prime)

		yield from detail_display ("Merkle Root", raw_block["merkleroot"])

		yield from detail_display ("Block Hash", blockhash_link (raw_block["hash"]), html=True)

		yield """<div class="blocknav">"""

		def a(n="prev", m="previous"):
			yield """<div class="blocknav_{n}">""".format(n=n)
			if m + "blockhash" in raw_block:
				yield '<a href="?block_hash=' + raw_block[m + "blockhash"]+"\" title='View "+m+" block'>"
			yield m + " block"
			if m + "blockhash" in raw_block:
				yield "</a>"
			yield "</div>"
		yield from a()
		yield from a("next","next")

		yield """
			<div class="blocknav_news">
				Block Time: """ + strtoout(raw_block["time"]) + """
			</div>
		</div>
		<div class="section_head">
			Transactions In This Block
		</div>
		<div class="txlist_wrap">
		"""

		for index,tx in enumerate(raw_block["tx"]):
			yield """<div class="txlist_showtx" id="showtx_{index}">
				<a href="?transaction={tx}" title="Transaction Details">
					{tx}
				</a>
			</div>""".format(index=index, tx=tx)

		yield "</div>"

def tx_detail(tx_id):
		raw_tx = bc_daemon.getrawtransaction (tx_id)
		yield from section_head ("Transaction: "+raw_tx["txid"])
		yield from section_subhead ("Detailed Description")
		yield from detail_display ("TX Version", raw_tx["version"])
		yield from detail_display ("TX Time", strtoout (raw_tx["time"]))
		yield from detail_display ("Lock Time", raw_tx["locktime"])
		yield from detail_display ("Confirmations", raw_tx["confirmations"])
		yield from detail_display ("Block Hash", blockhash_link (raw_tx["blockhash"]), html=True)
		yield from detail_display ("HEX Data", raw_tx["hex"])
		yield from section_head ("Transaction Inputs")
		for key,txin in enumerate(raw_tx["vin"]):
			yield from section_subhead ("Input Transaction {0}".format(key))
			if "coinbase" in txin:
				yield from detail_display ("Coinbase", txin["coinbase"])
				yield from detail_display ("Sequence", txin["sequence"])
			else:
				yield from detail_display ("TX ID", tx_link (txin["txid"]), html=True)
				yield from detail_display ("TX Output", txin["vout"])
				yield from detail_display ("TX Sequence", txin["sequence"])
				yield from detail_display ("Script Sig (ASM)", txin["scriptSig"]["asm"])
				yield from detail_display ("Script Sig (HEX)", txin["scriptSig"]["hex"])

		section_head ("Transaction Outputs")
		for key, txout in enumerate(raw_tx["vout"]):
			yield from section_subhead ("Output Transaction {0}".format(key))
			yield from detail_display ("TX Value", txout["value"])
			yield from detail_display ("TX Type", txout["scriptPubKey"]["type"])
			yield from detail_display ("Required Sigs", txout["scriptPubKey"]["reqSigs"])
			yield from detail_display ("Script Pub Key (ASM)", txout["scriptPubKey"]["asm"])
			yield from detail_display ("Script Pub Key (HEX)", txout["scriptPubKey"]["hex"])
			if "addresses" in txout["scriptPubKey"]:
				for key, address in enumerate(txout["scriptPubKey"]["addresses"]):
					yield from detail_display ("Address {0}".format(key), address)

		yield from section_head ("Raw Transaction Detail")

		yield '<textarea name="rawtrans" rows="25" cols="80" style="text-align:left;">'
		yield cgi.escape(json.dumps(raw_tx,indent=4))
		yield "</textarea>"

def detail_display (title, data, html=False):
		yield """<div class="detail_display">
			<div class="detail_title">
				{title}
			</div>
		""".format(title=title)

		yield """<div class="detail_data">
			{data}
		</div>""".format(data=data if html else "&shy;".join(cgi.escape(x) for x in textwrap.wrap(str(data), 50)))
		yield "</div>"
		yield "<div style='clear:both'></div>"

def tx_link (tx_id):
	return """<a href="?transaction={tx_id}" title="View Transaction Details">{tx_id}</a>""".format(tx_id=tx_id)

def blockheight_link (block_height):
	return """<a href="?block_height={block_height}" title="View Block Details">{block_height}</a>""".format(block_height=block_height)

def blockhash_link (block_hash):
	return """<a href="?block_hash={block_hash}" title="View Block Details">{block_hash}</a>""".format(block_hash=block_hash)

def section_head (heading):
	return """<div class="section_head">
		{heading}
	</div>""".format(heading=heading)

def section_subhead (heading):
	return """<div class="section_subhead">
		{heading}
	</div>""".format(heading=heading)
