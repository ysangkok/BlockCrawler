import bc_daemon
import base64
import html
import textwrap
import datetime
import time
import json
import urllib.parse
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
				Donations: RTvFbTNfhurjiLPzZia1djJ7sUWVA6EtEe<br>
				Github: <a href="http://github.com/ysangkok/BlockCrawler">http://github.com/ysangkok/BlockCrawler</a>
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
			factorization_delta, primes = next(get_primes_from_block(raw_block))
			factorization, delta = factorization_delta
			wrapnum = lambda i: "&shy;".join(textwrap.wrap(str(i), 50))
			factorlist = " &times; ".join("{}<sup>{}</sup>".format(wrapnum(i), j) if j != 1 else wrapnum(i) for i,j in factorization)
			factorlist += " + {}".format(wrapnum(delta))
			yield from detail_display("n", factorlist, htm=True)

			common_query = " * ".join("{}^{}".format(i, j) if j != 1 else str(i) for i,j in factorization)
			common_query += " + {}".format(delta)
			offsets = [str(t[0]) for t in primes]
			comma_joined = ",".join(offsets)

			wolframalpha_query = "isprime(x + " + common_query + ") where x=" + comma_joined

			gamma_query = "n = " + common_query.replace("^","**") + "\n#--\n[isprime(x + n) for x in [" + comma_joined + "]]\n#--"
			htm = "<a href='http://wolframalpha.com/input/?i={}'>WolframAlpha</a>".format(html.escape(urllib.parse.quote_plus(wolframalpha_query)))
			htm += " <a href='http://live.sympy.org/?evaluate={}'>SymPy Live</a>".format(html.escape(urllib.parse.quote_plus(gamma_query)))

			maxima_query = "x: " + common_query + ";\nprimep(x + " + ");\nprimep(x + ".join(offsets) + ");\n"

			htm += " <a href='http://maxima-online.org/#?in={}'>Maxima-Online</a>".format(html.escape(urllib.parse.quote_plus(maxima_query)))

			src = """
package main

import "fmt"
import "math/big"

func main() {
	bi := big.NewInt(0)
	line := \"""" + str(primes[0][1]) + """\"
	
	if _, ok := bi.SetString(line, 10); !ok {
            fmt.Printf("couldn't interpret", line)
        }
	
	fmt.Println(bi.ProbablyPrime(2))
	bi = bi.Add(bi, big.NewInt(4))
	fmt.Println(bi.ProbablyPrime(2))
	bi = bi.Add(bi, big.NewInt(2))
	fmt.Println(bi.ProbablyPrime(2))
	bi = bi.Add(bi, big.NewInt(4))
	fmt.Println(bi.ProbablyPrime(2))
	bi = bi.Add(bi, big.NewInt(2))
	fmt.Println(bi.ProbablyPrime(2))
	bi = bi.Add(bi, big.NewInt(4))
	fmt.Println(bi.ProbablyPrime(2))
}
"""

			htm += " <a href='javascript:void(0)' onclick='document.forms[0].submit(); return false;'>Test with Go</a> (<a href='data:text/plain;base64,{}'>program text</a>)<form target='_blank' action='http://play.golang.org/compile' method='POST'><input type='hidden' name='version' value='2'><input type='hidden' name='body' value='{}'></form>".format(html.escape(urllib.parse.quote(base64.b64encode(src.encode("utf-8")).decode("ascii"))), html.escape(src))

			yield from detail_display("Check primality", htm, htm=True)

			for offset, prime in primes:
				yield from detail_display("Prime n+{}".format(offset), prime)

		yield from detail_display ("Merkle Root", raw_block["merkleroot"])

		yield from detail_display ("Block Hash", blockhash_link (raw_block["hash"]), htm=True)

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
		try:
			raw_tx = bc_daemon.getrawtransaction (tx_id)
		except Exception as e:
			yield from section_head(str(e))
			return
		yield from section_head ("Transaction: "+raw_tx["txid"])
		yield from section_subhead ("Detailed Description")
		yield from detail_display ("TX Version", raw_tx["version"])
		yield from detail_display ("TX Time", strtoout (raw_tx["time"]))
		yield from detail_display ("Lock Time", raw_tx["locktime"])
		yield from detail_display ("Confirmations", raw_tx["confirmations"])
		yield from detail_display ("Block Hash", blockhash_link (raw_tx["blockhash"]), htm=True)
		yield from detail_display ("HEX Data", raw_tx["hex"])
		yield from section_head ("Transaction Inputs")
		for key,txin in enumerate(raw_tx["vin"]):
			yield from section_subhead ("Input Transaction {0}".format(key))
			if "coinbase" in txin:
				yield from detail_display ("Coinbase", txin["coinbase"])
				yield from detail_display ("Sequence", txin["sequence"])
			else:
				yield from detail_display ("TX ID", tx_link (txin["txid"]), htm=True)
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
		yield html.escape(json.dumps(raw_tx,indent=4))
		yield "</textarea>"

def detail_display (title, data, htm=False):
		yield """<div class="detail_display">
			<div class="detail_title">
				{title}
			</div>
		""".format(title=title)

		yield """<div class="detail_data">
			{data}
		</div>""".format(data=data if htm else "&shy;".join(html.escape(x) for x in textwrap.wrap(str(data), 50)))
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
