from engines.fast_scraper import Twitter
from twscrape import API
import asyncio

next_team = Twitter(
    api=API(), 
    sources = ["ShamsCharania"], 
    name="next_team",
    prompt = "Rule Your default output for all text is exactly Nothing Important You must only change this output to the format Player Name, Team Name if the text explicitly confirms a completed signing or trade where a player joins a team If a player is being waived released bought out or leaving a team without a team confirmed you must output exactly Nothing Important Never extract a player name or use a comma if they are just leaving a team or if the team is missing Examples Text Celtics sign Jrue Holiday Output Jrue Holiday, Boston Celtics Text Nets waive Carter Ellis Output Nothing Important Text Suns part ways with Jordan Pierce Output Nothing Important",
    decline_words=["offer sheet", "right to match", "days to match", "hours to match", "matching period", "in talks", "discussing", "exploring", "monitoring", "checking in on", "gauging interest", "expressed interest", "linked to", "eyeing", "mutual interest", "floated", "downplay", "denies", "denied", "shot down", "no truth to", "quashed", "not expected to be traded", "will finish out his contract", "bought out", 'buyout', "collapsed", "stalled", "unlikely", "remains unclear"]
)

# =====================================================================
# NEGATIVE TESTS (Lists 1-5): MUST ALWAYS RETURN 'Nothing Important'
# =====================================================================

# LEVEL 1: Clean Noise & Baseline Speculation
# Objective: Standard rumor/interest tweets with clean syntax.
TEST_L1_SIMPLE_SPECULATION = [
    "The Boston Celtics are considered a strong suitor for free agent forward Terrance Flint this summer.",
    "There is growing league speculation that the Philadelphia 76ers will make a hard push for guard Devon Brooks.",
    "The Sacramento Kings are internally discussing a potential trade package to target center Julian Vance.",
    "Free agent wing Marcus Boyd is expected to generate significant interest from the Portland Trail Blazers.",
    "The New York Knicks have held exploratory conversations regarding forward Elijah Vance, sources say.",
    "League executives believe the Cleveland Cavaliers are positioned to pursue guard Cameron Drake in free agency.",
    "The Milwaukee Bucks are keeping a close eye on the developing situation surrounding forward Austin Vance.",
    "Sources indicate the Minnesota Timberwolves have checked out the potential trade market for center Ian Vance.",
    "The Oklahoma City Thunder are projected to have interest in veteran guard Sterling Vance if he hits the market.",
    "The Golden State Warriors are prioritizing adding an experienced wing player like free agent Silas Vance."
]

# LEVEL 2: Typical Shams Style Negatives (AVERAGE RUMOR DIFFICULTY)
# Objective: Adds insider vernacular ("monitoring", "due diligence", "sources tell ESPN") to test boundary defense.
TEST_L2_SHAMS_RUMORS = [
    "Sources: The Miami Heat are expressing strong exploratory trade interest in acquiring guard Collin Vance, though no formal offer has been extended yet.",
    "The Phoenix Suns are continuing to intensely monitor and evaluate free agent center Roman Vance as a potential frontcourt depth piece, league sources say.",
    "The Dallas Mavericks have held ongoing internal discussions regarding a potential trade package for forward Xavier Ross, but talks remain completely preliminary.",
    "Several Eastern Conference contenders have registered initial trade interest in forward Tyson Vance, including the Atlanta Hawks, according to league sources.",
    "The Los Angeles Lakers continue to do background work and extensive due diligence on guard Silas Vance but have yet to enter serious contract talks.",
    "The Houston Rockets are checking in on the availability of forward Marcus Vance, though current talks lack serious traction, sources tell The Athletic.",
    "As free agency nears, the Memphis Grizzlies are expected to gauge the trade value of guard Christian Moss, according to league executives.",
    "Sources: The Chicago Bulls are registering exploratory interest in unrestricted free agent wing Malik Vance as a bench scoring option.",
    "The Denver Nuggets remain engaged in fluid internal discussions regarding forward Derek Hodge, but no official framework has materialized.",
    "League sources indicate the Toronto Raptors are monitoring contract extensions elsewhere, keeping tabs on guard Wesley Vance as a potential target."
]

# LEVEL 3: Complex Narrative / Multi-Team Speculation (HIGH RUMOR DIFFICULTY)
# Objective: Dense paragraphs tracking multiple names, assets, and contingencies without a completed transaction.
TEST_L3_NARRATIVE_SPECULATION = [
    "While the Atlanta Hawks have prioritized perimeter defense in trade frameworks involving forward Tyson Vance, a secondary market has materialized consisting of exploratory calls from both the Knicks and Heat.",
    "As the contract deadline approaches for guard Christian Moss, internal pressure is mounting within the Memphis front office to explore sign-and-trade avenues rather than losing the veteran guard for nothing, sources say.",
    "The Portland Trail Blazers have held preliminary conversations regarding a draft-night package centered on center Deandre Vance, though opposing executives describe the current asking price as prohibitively high.",
    "Sources tell ESPN that while the Utah Jazz remain enamored with the long-term analytical profile of forward Bradley Vance, they are concurrently listening to soft inquiries from multiple Western Conference playoff teams.",
    "The Charlotte Hornets are expected to aggressively pursue backcourt upgrades once the market opens, with league sources pointing to unrestricted free agent guard Dominic Vance as a primary target on their board.",
    "Despite widespread external speculation linking All-Star guard Malik Vance to a potential big-market destination, the Indiana Pacers have given zero indication they intend to entertain trade offers at this juncture.",
    "The Detroit Pistons are keeping a close watch on the unfolding contract standoff between the Orlando Magic and forward Trevor Jenkins, positioning themselves to pounce if negotiations completely stall.",
    "Sources close to the situation indicate that while guard Wesley Vance has drawn exploratory tire-kicking from the Cleveland Cavaliers, serious traction remains heavily dependent on structural cap clearance.",
    "The Minnesota Timberwolves have held fluid, low-level internal discussions regarding veteran forward Nolan Vance, mapping out potential trade exceptions that could theoretically absorb his salary filler.",
    "A potential sign-and-trade framework that would send forward Corey Vance to a title contender remains entirely speculative as cap sheet hard-caps complicate the required transaction geometry, sources say."
]

# LEVEL 4: Team-Initiated Departures & Drops
# Objective: Test if the model resists pulling out the current team name when a player is dropped or bought out.
TEST_L4_DEPARTURES_NO_NEW_TEAM = [
    "The Charlotte Hornets have officially waived guard Dominic Vance after one season with the franchise.",
    "Veteran forward Preston Vance has been released by the Washington Wizards, league sources confirm.",
    "The Utah Jazz have reached a formal contract buyout agreement with center Deandre Vance, sources say.",
    "Sources: The Orlando Magic have announced the immediate release of wing Kendrick Vance from the roster.",
    "Guard Christian Vance has cleared unconditional waivers following his official release from the Brooklyn Nets.",
    "The Portland Trail Blazers have filed the required league paperwork to waive forward Julian Vance.",
    "Center Alec Vance has officially parted ways with the New Orleans Pelicans after clearing waivers.",
    "Sources: The Indiana Pacers have terminated the remaining contract of veteran guard Wesley Vance.",
    "Forward Bradley Vance has agreed to a contract buyout with the Detroit Pistons, league sources tell ESPN.",
    "The Minnesota Timberwolves have officially waived wing Spencer Vance ahead of the contract guarantee deadline."
]

# LEVEL 5: Adversarial Structural Traps & Final-Stage Collapses
# Objective: The ultimate negative stress test. The text contains words like "agreed", "finalized", and "trade package", but explicitly states the transaction fell through.
TEST_L5_ADVERSARIAL_COLLAPSE = [
    "The lucrative sign-and-trade agreement designed to send guard Brendan Vance to a Western Conference contender has completely stalled at the eleventh hour, league sources report.",
    "The complex multi-team trade framework that was meticulously built to relocate forward Silas Vance to a new destination has completely fallen apart at the signature stage, sources say.",
    "Free agent guard Anton Vance has agreed in principle to sign a maximum contract extension, though his target team remains entirely undecided as market options shift.",
    "The sweeping trade package that would have successfully sent forward Trevor Vance to the Boston Celtics has officially collapsed over physical tracking data concerns, sources say.",
    "Center Malik Vance has finalized a highly complex contract agreement with his agency to switch primary representation ahead of his upcoming unrestricted free agency cycle.",
    "Sources: Guard Desmond Vance is prepared to sign a lucrative contract extension with an unnamed Eastern Conference suitor immediately once the midnight tampering window opens.",
    "If he successfully passes his upcoming physical examination next Monday, forward Corey Vance is heavily expected to finalize a deal with a new team, according to his agent.",
    "Free agent forward Nolan Vance has announced his formal intention to sign a contract with a title contender by the conclusion of the upcoming weekend, sources indicate.",
    "The ongoing, high-stakes contract extension negotiations involving center Elias Vance and his current team have officially broken down with no resolution in sight.",
    "Guard Wesley Vance has cleared his background check and received formal league clearance to sign a contract, though no front office has stepped up with a formal offer."
]


# =====================================================================
# POSITIVE TESTS (Lists 6-10): MUST ALWAYS EXTRACT 'Player Name, Team Name'
# =====================================================================

# LEVEL 6: Bare-Bones Basic Confirmations
# Objective: Simple, clear, active-voice completed transactions with zero syntactic noise.
TEST_L6_SIMPLE_CONFIRMED = [
    "Free agent guard Marcus Vance has signed a two-year contract with the Atlanta Hawks.",
    "The Denver Nuggets have finalized a trade to acquire forward Derek Hodge from the Wizards.",
    "Center Kaleb Vance has agreed to a four-year maximum contract extension with the Miami Heat.",
    "Free agent wing Xavier Thorne has signed a one-year veteran minimum contract with the Phoenix Suns.",
    "The Detroit Pistons have officially acquired guard Jalen Ross in a trade with the Rockets.",
    "Forward Brandon Cole has agreed to a three-year, $36 million deal with the Indiana Pacers.",
    "The Memphis Grizzlies have finalized a sign-and-trade agreement to acquire guard Christian Moss.",
    "Free agent center Damian Vance has signed a two-year contract with the Utah Jazz, sources say.",
    "The Toronto Raptors have signed forward Trevor Jenkins to a multi-year contract extension.",
    "Guard Malik Vance has officially finalized a one-year agreement to join the Chicago Bulls."
]

# LEVEL 7: Typical Shams Style Positives (AVERAGE CONFIRMATION DIFFICULTY)
# Objective: Standard transactional reporting complete with financial metrics and agency tags.
TEST_L7_SHAMS_CONFIRMATIONS = [
    "Free agent forward Jaren Brooks has agreed to a four-year, $84 million contract with the Detroit Pistons, his agent tells ESPN. A massive frontcourt addition for Detroit.",
    "Guard Deonte Vance has agreed to a two-year, $12 million contract extension with the Sacramento Kings, league sources tell The Athletic. Kings secure their backcourt depth.",
    "Free agent wing Tristian Vance has agreed to a one-year, fully guaranteed contract with the Milwaukee Bucks, sources tell ESPN. Vance provides veteran bench scoring.",
    "All-Star guard Kaelen Montgomery has finalized a five-year, maximum contract extension with the Oklahoma City Thunder, his agent tells The Athletic. A massive cornerstone signing.",
    "Free agent center Damian Vance has agreed to a three-year contract with the New York Knicks, sources tell ESPN. Vance heads to New York to bolster their interior defense.",
    "Seeking structural stability, veteran guard Anton Vance has ultimately agreed to a two-year deal with the Boston Celtics, Klutch Sports agents confirm to The Athletic.",
    "Choosing stability over shifting markets, forward Trevor Vance has finalized a three-year contract extension with the Memphis Grizzlies, according to his representation at CAA.",
    "Following an impressive showcase in the Summer League, undrafted free agent center Malik Vance has secured a fully guaranteed roster spot and signed with the Utah Jazz.",
    "Seeking a prominent backend role on a rebuilding roster, veteran wing Julian Vance has agreed to a one-year deal with the Charlotte Hornets, Priority Sports agents confirm.",
    "Capitalizing on a career-best shooting season, free agent guard Brendan Vance has agreed to a four-year, $52 million contract with the Orlando Magic, Lift Sports agents tell ESPN."
]

# LEVEL 8: Multi-Player Trade Environments
# Objective: Dense trade architectures where the model must successfully isolate the player landing at the specified target team amidst outgoing matching salary assets.
TEST_L8_MULTI_PLAYER_TRADES = [
    "The Phoenix Suns have finalized a blockbuster trade to acquire guard Bradley Vance from the Washington Wizards in exchange for a package centered around draft capital, sources tell ESPN.",
    "The Golden State Warriors have acquired forward Christian Vance from the Toronto Raptors as part of a multi-team deal involving future protected second-round picks, sources say.",
    "Sources: The New York Knicks have finalized a trade to acquire center Andre Vance from the Minnesota Timberwolves, sending draft assets out in the transaction.",
    "The Los Angeles Clippers have acquired guard Devon Vance from the Portland Trail Blazers in exchange for matchable salary filler and cash considerations, league sources confirm.",
    "The Brooklyn Nets have finalized a trade agreement to acquire forward Jalen Vance from the Houston Rockets, absorbing his contract into an existing trade exception.",
    "Sources: The Atlanta Hawks have acquired center Marcus Vance from the Dallas Mavericks, finalizing a deal that had been active in discussions over the last week.",
    "The Chicago Bulls have finalized a trade to acquire guard Sterling Vance from the Sacramento Kings in exchange for future draft considerations, sources tell The Athletic.",
    "Forward Roman Vance has officially been acquired by the Cleveland Cavaliers in a completed trade with the Charlotte Hornets, according to league sources.",
    "The New Orleans Pelicans have finalized an agreement to acquire guard Tyson Vance from the Indiana Pacers, adding immediate defensive versatility to their perimeter.",
    "Sources: The Milwaukee Bucks have finalized a trade to acquire veteran forward Silas Vance from the San Antonio Spurs to bolster their depth for a postseason run."
]

# LEVEL 9: Heavy Contextual, Medical & Analytical Noise
# Objective: The transaction is confirmed, but it is deeply buried under long narratives detailing ACL tears, shooting percentages, or physical evaluations.
TEST_L9_ANALYTICAL_CONTEXT = [
    "Coming off a devastating ACL tear that sidelined him for the entire prior season, free agent guard Anton Vance has agreed to a one-year comeback contract with the Miami Heat.",
    "Boasting a career-high 42 percent mark from beyond the three-point arc last season, forward Trevor Vance has finalized a lucrative four-year extension with the Sacramento Kings.",
    "Despite seeing his defensive metrics decline slightly over the past calendar year, veteran center Malik Vance has agreed to a two-year deal with the Dallas Mavericks.",
    "Averages of 18 points and 6 assists per game in the secondary market have paid off as guard Desmond Vance finalizes a three-year contract with the Brooklyn Nets.",
    "Finishing third overall in the league's Sixth Man of the Year voting metrics, free agent forward Corey Vance has agreed to a three-year deal with the Toronto Raptors.",
    "After undergoing successful arthroscopic knee surgery earlier this offseason, free agent guard Brendan Vance has signed a fully guaranteed one-year contract with the Utah Jazz.",
    "Regarded by league analysts as one of the premier perimeter lock-down defenders available, forward Nolan Vance has finalized a contract extension with the Memphis Grizzlies.",
    "Providing elite spacing with an analytical profile that fits their fast-pace offense, free agent center Elias Vance has signed a two-year contract with the Indiana Pacers.",
    "Despite initial medical concerns raised during the physical assessment phase, guard Wesley Vance has officially signed a one-year contract with the Houston Rockets.",
    "As an advanced data darling who led his team in net rating swing, free agent forward Silas Vance has finalized a three-year contract with the Chicago Bulls."
]

# LEVEL 10: Historical Flashbacks / The "Champagnie Loophole" (MAX CONFIRMATION DIFFICULTY)
# Objective: The absolute peak difficulty for small models. The text starts with historical verbs ("waived", "released", "cut", "bought out") but ends with a current, active team confirmation.
TEST_L10_HISTORICAL_FLASHBACKS = [
    "Waived three seasons ago and forced to grind out a career path through the G League, guard Anton Vance has signed a multi-year deal with the San Antonio Spurs.",
    "Originally traded away by the franchise as salary filler early in his career, forward Trevor Vance has returned to sign a two-year contract with the Los Angeles Lakers.",
    "Just months after being cut and bought out by his hometown team, veteran center Malik Vance has revitalized his career and signed a one-year deal with the Denver Nuggets.",
    "Drafted in the second round and subsequently released by two different franchises, guard Desmond Vance has finalized a guaranteed contract with the Philadelphia 76ers.",
    "Having cleared waivers entirely unnoticed just one calendar year ago, breakout forward Corey Vance has signed a lucrative three-year contract extension with the Orlando Magic.",
    "Following a formal contract termination that left his future in the league highly uncertain, guard Brendan Vance has officially signed a one-year deal with the Boston Celtics.",
    "Once considered an untradeable asset before being waived by a rebuilding squad, veteran forward Nolan Vance has signed a veteran minimum contract with the Phoenix Suns.",
    "After an abrupt release from his previous roster forced him into unrestricted free agency, center Elias Vance has finalized a two-year deal with the Golden State Warriors.",
    "Years after a high-profile trade request collapsed and saw him waived, veteran guard Wesley Vance has signed a short-term deal to join the Cleveland Cavaliers.",
    "Bouncing back seamlessly from a tough buyout situation that halted his momentum, forward Silas Vance has agreed to a two-year contract with the New York Knicks."
]

# COMBINED MASTER DATASET
master = [
    TEST_L1_SIMPLE_SPECULATION, TEST_L2_SHAMS_RUMORS, TEST_L3_NARRATIVE_SPECULATION,
    TEST_L4_DEPARTURES_NO_NEW_TEAM, TEST_L5_ADVERSARIAL_COLLAPSE, TEST_L6_SIMPLE_CONFIRMED,
    TEST_L7_SHAMS_CONFIRMATIONS, TEST_L8_MULTI_PLAYER_TRADES, TEST_L9_ANALYTICAL_CONTEXT,
    TEST_L10_HISTORICAL_FLASHBACKS
]


async def main():
    for index, list in enumerate(master):
        f = []
        for tweet in list:
            message = (await next_team.get_ai_response(tweet))
            f.append(message)
        print(f'\n\n{index}: {f}')
async def other():
    next_team.get_ai_response()

asyncio.run(main())