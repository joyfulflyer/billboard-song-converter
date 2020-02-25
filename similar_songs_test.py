import unittest
from collections import namedtuple

from similar_songs import further_comparison_checks


class TestSimilarSongHandling(unittest.TestCase):

    TestEntry = namedtuple("TestEntry", ["name", "artist"])

    def test_compare_values(self):
        for entry, result, _, expected in test_set:
            e = self.TestEntry(entry[0], entry[1])
            r = self.TestEntry(result[0], result[1])
            with self.subTest():
                self.assertEqual(further_comparison_checks(e, r), expected,
                                 f"Entry: {entry} Result: {result}")

    def test_returns_boolean(self):
        entry = self.TestEntry("hello", "artist")
        self.assertIs(type(further_comparison_checks(entry, entry)), bool)

    def test_call_with_same_data_returns_true(self):
        entry = self.TestEntry("hello", "artist")
        search = self.TestEntry(["hello"], ["artist"])
        self.assertTrue(further_comparison_checks(entry, search))

    def test_call_with_different_data_returns_false(self):
        first = self.TestEntry("hello", "artist")
        second = self.TestEntry("moo", "food")
        self.assertFalse(further_comparison_checks(first, second))

    def test_different_punctuation_ok(self):
        first = self.TestEntry("Are You Lonesome Tonight", "Elvis Presley")
        second = self.TestEntry(["Are You Lonesome Tonight?"],
                                ["Elvis Presley"])
        self.assertTrue(further_comparison_checks(first, second))

    # At least for now, we are assuming the curly brackets
    # do not designate any song identifying information
    def test_ignore_data_in_curly_brackets(self):
        first = self.TestEntry("Apple Green {1991}", "Milltown Brothers")
        second = self.TestEntry(["Apple Green"], ["Milltown Brothers"])
        self.assertTrue(further_comparison_checks(first, second))

    def test_drop_featuring_words(self):
        first = self.TestEntry("Area Codes", "Ludacris Ft Nate Dogg")
        second = self.TestEntry(["Area Codes"],
                                ["Ludacris Featuring Nate Dogg"])
        self.assertTrue(further_comparison_checks(first, second),
                        f"Entry: {first} Search: {second} should be true")

    # Not sure about this, maybe remove or change one to the other?
    def test_handle_and(self):
        first = self.TestEntry("Baby I'm Scared Of You", "Womack And Womack")
        second = self.TestEntry(["Baby I'm Scared Of You"],
                                ["Womack & Womack"])
        self.assertTrue(further_comparison_checks(first, second))

    def test_handle_odd_spacing(self):
        first = self.TestEntry("Baby I'm-a Want You", "Bread")
        second = self.TestEntry(["Baby I'm - A Want You"], ["Bread"])
        self.assertTrue(further_comparison_checks(first, second))

    def test_second_set(self):
        for entry, result, _, expected in set_2:
            e = self.TestEntry(entry[0], entry[1])
            r = self.TestEntry(result[0], result[1])
            with self.subTest():
                self.assertEqual(further_comparison_checks(e, r), expected,
                                 f"Entry: {entry} Result: {result}")


#((entry.name, entry.artist), (result.name, result.artist), score)
# Clearly not a random set :)
test_set = [
    (("Apologize", "Timbaland Ft One Republic"),
     (["Apologize"], ["Timbaland Ft One Republic"]), 23.610912, True),
    (("Apologize", "Timbaland Pts One Republic"),
     (["Apologize"], ["Timbaland Ft One Republic"]), 22.096218, False),
    (("Apologize", "Timbaland Pts Onerepublic"),
     (["Apologize"], ["Timbaland Featuring OneRepublic"]), 20.122234, False),
    (("Apologize", "Timbaland Ft Onerepublic"),
     (["Apologize"], ["Timbaland Featuring OneRepublic"]), 0, True),
    (("Apologize", "Timbaland Feat Onerepublic"),
     (["Apologize"], ["Timbaland Featuring OneRepublic"]), 0, True),
    (("Apologize", "Timbaland Ft One republic"),
     (["Apologize"], ["Timbaland Featuring OneRepublic"]), 0, True),
    (("Apparently Nothin' {1991 Re-release}", "Young Disciples"),
     (["Apparently Nothin'"], ["Young Disciples"]), 27.597462, True),
    (("Apple Green {1991}", "Milltown Brothers"),
     (["Apple Green"], ["Milltown Brothers"]), 25.278244, True),
    (("Aquarius/Let The Sunshine In (The Flesh Failures)",
      "The 5th Dimension"), (["Aquarius/Let The Sunshine In"],
                             ["The 5th Dimension"]), 31.251286, False),
    (("Aquarius/let The Sunshine In", "5Th Dimension"),
     (["Aquarius/Let The Sunshine In"], ["The 5th Dimension"
                                         ]), 28.574797, True),
    (("Aquarius/let The Sunshine In", "The Fifth Dimension"),
     (["Aquarius/Let The Sunshine In"],
      ["The 5th Dimension"]), 26.086386, False),  # At least for v1
    (("Are You Dreaming? Ft Captain Hollywood",
      "Twenty4Seven Featuring Captain Hollywood"),
     (["I Can't Stand It Ft Captain Hollywood"],
      ["Twenty4Seven Featuring Captain Hollywood"]), 27.288927, False),
    (("Are You Getting Enough Of What Makes You Happy", "Hot Chocolate"),
     (["Are You Getting Enough Happiness"], ["Hot Chocolate"
                                             ]), 26.426823, False),
    (("Are You Happy Now", "Michelle Branch"),
     (["Are You Happy Now?"], ["Michelle Branch"]), 25.46182, True),
    (("Are You Lonesome Tonight", "Elvis Presley"),
     (["Are You Lonesome Tonight?"], ["Elvis Presley"]), 24.478643, True),
    (("Are You Lonesome Tonight", "Elvis Presley With The Jordanaires"),
     (["Are You Lonesome Tonight?"], ["Elvis Presley"]), 24.478643,
     False),  # At least for the first iteration
    (("Are You Lonesome Tonight? (live)", "Elvis Presley"),
     (["Are You Lonesome Tonight?"], ["Elvis Presley"]), 24.478643, False),
    (("Are You Lonesome Tonight? {1977}", "Elvis Presley"),
     (["Are You Lonesome Tonight?"], ["Elvis Presley"]), 24.478643, True),
]

set_2 = [
    (("Are You Man Enough", "Uno Clio Ft Martine Mccutcheon"),
     (["Are You Man Enough"], ["Uno Clio"]), 28.009714, False),
    (("Are You Sure Hank Done It This Way/bob Wills Is Th", "Waylon Jennings"),
     (["Are You Sure Hank Done It This Way"], ["Waylon Jennings"
                                               ]), 34.55643, False),
    (("Area Codes", "Ludacris Ft Nate Dogg"),
     (["Area Codes"], ["Ludacris Featuring Nate Dogg"]), 33.27855, True),
    (("Arms Around You", "Xxxtentacion/Pump/Maluma/Swae"),
     (["Arms Around You"],
      ["XXXTENTACION x Lil Pump Featuring Maluma & Swae Lee"
       ]), 23.395634, False),
    (("Around The Way Girl/mama Said", "Ll Cool J"),
     (["Around The Way Girl"], ["LL Cool J"]), 24.467806, False),
    (("Around The World", "Natalie La Rose Ft Fetty Wap"),
     (["Around The World"], ["Natalie La Rose Featuring Fetty Wap"
                             ]), 24.209156, True),
    (("Arthur's Theme (the Best That You Can Do)", "Christopher Cross"),
     (["Arthur's Theme (Best That You Can Do)"], ["Christopher Cross"
                                                  ]), 34.46467, True),
    (("As Long As You Love Me", "Justin Bieber Ft Big Sean"),
     (["As Long As You Love Me"], ["Justin Bieber Featuring Big Sean"
                                   ]), 31.74562, True),
    (("As Long As You Love Me (Acoustic)", "Justin Bieber"),
     (["As Long As You Love Me"], ["Justin Bieber Featuring Big Sean"
                                   ]), 27.729881, False),
    (("As Your Friend", "Afrojack Ft Chris Brown"),
     (["As Your Friend"], ["Afrojack Featuring Chris Brown"
                           ]), 23.930288, True),
    (("Ashes To Ashes", "Mindbenders"),
     (["Ashes To Ashes"], ["The Mindbenders"]), 31.762012, True),
    (("Ass Back Home", "Gym Class Heroes Ft Neon Hitch"),
     (["Ass Back Home"], ["Gym Class Heroes Featuring Neon Hitch"
                          ]), 32.34549, True),
    (("At The Club/saturday Night At The Movies", "The Drifters"),
     (["Saturday Night At The Movies"], ["The Drifters"]), 33.330772, False),
    (("At The Club/saturday Night At The Movies {1972}", "The Drifters"),
     (["Saturday Night At The Movies"], ["The Drifters"]), 33.330772, False),
    (("At The Top Of The Stairs", "Formations"),
     (["At The Top Of The Stairs"], ["The Formations"]), 29.022585, True),
    (("At This Moment", "Billy Vera And The Beaters"),
     (["At This Moment"], ["Billy & The Beaters"
                           ]), 25.520048, False),  # How about 'and'?
    (("Atomic Dog", "George Clinton"),
     (["Atomic Dog"], ["George Clinton Featuring Coolio"]), 24.881117, False),
    (("Ava Adore", "Smashing Pumpkins"),
     (["Ava Adore"], ["The Smashing Pumpkins"]), 30.889868, True),
    (("Avenues & Alleyways", "Tony Christie"),
     (["Avenues And Alleyways"], ["Tony Christie"]), 29.316208, True),
    (("Ayo Technology", "50 Cent/Justin Timberlake"),
     (["Ayo Technology"], ["50 Cent Featuring Justin Timberlake & Timbaland"
                           ]), 33.509483, False),
    (("Ayo Technology", "50 Cent/Timberlake/Timbaland"),
     (["Ayo Technology"], ["50 Cent Featuring Justin Timberlake & Timbaland"
                           ]), 34.015205, False),
    (("Babushka Boi", "Asap Rocky"), (["Babushka Boi"], ["A$AP Rocky"]),
     28.824451, False),  # Bleh, leetspeak
    (("Baby 1 More Time", "Britney Spears"), (["...Baby One More Time"],
                                              ["Britney Spears"]), 20.426449,
     False),  # Also numbers
    (("Baby Baby Bye Bye", "Jerry Lee Lewis"),
     (["Baby, Bye Bye"], ["Dickey Lee"]), 33.12935, False),
    (("Baby Be Mine Ft Teddy Riley", "Blackstreet Featuring Teddy Riley"),
     (["Baby Be Mine (From 'CB4')"], ["BLACKstreet (Featuring Teddy Riley)"
                                      ]), 21.800598, False),
    (("Baby By Me", "50 Cent Ft Ne-Yo"),
     (["Baby By Me"], ["50 Cent Featuring Ne-Yo"]), 22.802681, True),
    (("Baby Come To Me", "Patti Austin And James Ingram"),
     (["Baby, Come To Me"], ["Patti Austin A Duet With James Ingram"
                             ]), 20.972834, False),
    (("Baby Don't Cry (Keep Ya Head Up II)", "2Pac + Outlawz"),
     (["Keep Ya Head Up"], ["2Pac"]), 25.941832, False),
    (("Baby Face", "Wing And A Prayer Fife And Drum Corps"),
     (["Baby Face"], ["The Wing And A Prayer Fife & Drum Corps."
                      ]), 29.256271, True),
    (("Baby I Love Your Way - Free Bird", "Will To Power"),
     (["Baby, I Love Your Way/Freebird Medley"], ["Will To Power"
                                                  ]), 21.735329, False),
    (("Baby I'm Scared Of You", "Womack And Womack"),
     (["Baby I'm Scared Of You"], ["Womack & Womack"]), 28.505117, True),
    (("Baby I'm-a Want You", "Bread"), (["Baby I'm - A Want You"], ["Bread"]),
     20.960228, True),
    (("Baby It's Cold Outside", "Brett Eldredge/Meghan Trainor"),
     (["Baby, It's Cold Outside"], ["Brett Eldredge Featuring Meghan Trainor"
                                    ]), 32.468742, True),
    (("Baby It's Cold Outside", "Dean Martin"),
     (["Baby, It's Cold Outside"], ["Dean Martin & Martina McBride"
                                    ]), 25.553116, False),
    (("Baby It's Cold Outside", "Idina Menzel Ft Michael Buble"),
     (["Baby It's Cold Outside"], ["Idina Menzel Duet With Michael Buble"
                                   ]), 30.669731, False),
    (("Baby It's You", "Jojo Ft Bow Wow"),
     (["Baby It's You"], ["JoJo Featuring Bow Wow"]), 20.871439, True)
    # (("Baby Make Your Own Sweet Music", "The Band"),
    #  ("Baby Make Your Own Sweet Music", "Jay And The Techniques"), 23.581142),
    # (("Baby Now That I've Found You", "Alison Krauss"),
    #  ("Baby, Now That I've Found You",
    #   "Alison Krauss + Union Station"), 27.818419),
    # (("Baby Now That I've Found You", "Foundations"),
    #  ("Baby, Now That I've Found You", "The Foundations"), 26.310692),
    # (("Baby When The Light", "David Guetta Ft Cozi"),
    #  ("Baby When The Light", "David Guetta"), 22.131702),
    # (("Baby's Coming Back/transylvania", "Mcfly"), ("Transylvania", "Mcfly"),
    #  20.522417),
    # (("Baby, Baby My Love Is All For You", "Deniece Williams"),
    #  ("Baby,baby My Love's All For You", "Deniece Williams"), 25.36974),
    # (("Baby, Don't You Cry <P6>(The New <P255>Swingova <P6>Rhythm)",
    #   "Ray Charles"), ("Baby, Don't You Cry (The New Swingova Rhythm)",
    #                    "Ray Charles and his Orchestra"), 29.5206),
    # (("Baby, I'm Hooked (Right Into Your Love)", "ConFunkShun"),
    #  ("Baby I'm Hooked", "ConFunkShun"), 22.63924),
    # (("Baby, I'm Yours/God Knows", "Debby Boone"),
    #  ("God Knows/Baby, I'm Yours", "Debby Boone"), 31.8676),
    # (("Baby, We Better Try And Get It Together", "Barry White"),
    #  ("Baby, We Better Try To Get It Together", "Barry White"), 28.405558),
    # (("Back And Forth", "Aaliyah"), ("Back & Forth", "Aaliyah"), 22.142097),
    # (("Back In Stride Ft Frankie Beverly", "Maze Featuring Frankie Beverly"),
    #  ("Back In Stride", "Maze Featuring Frankie Beverly"), 28.026226),
    # (("Back Like That", "Ghostface Killah Ft Ne-Yo"),
    #  ("Back Like That", "Ghostface Killah Featuring Ne-Yo"), 24.904984),
    # (("Back On My Feet Again", "Foundations"), ("Back On My Feet Again",
    #                                             "The Foundations"), 24.31654),
    # (("Back On The Chain Gang", "The Pretenders"), ("Back On The Chain Gang",
    #                                                 "Pretenders"), 26.654825),
    # (("Back Seat (Of My Jeep)/Pink Cookies In A Plastic Bag", "LL Cool J"),
    #  ("Back Seat (Of My Jeep)", "LL Cool J"), 33.550396),
    # (("Back To Life (However Do You Want Me)",
    #   "Soul II Soul (Featuring Caron Wheeler)"), ("Back To Life",
    #                                               "Soul II Soul"), 23.866823),
    # (("Back To Life (however Do You Want Me)", "Soul Ii Soul"),
    #  ("Back To Life", "Soul II Soul"), 23.866823),
    # (("Back To School Again", "The Four Tops"), ("Back To School Again",
    #                                              "Four Tops"), 24.942932),
    # (("Back To The Sixties Part 2", "Tight Fit"), ("Back To The Sixties",
    #                                                "Tight Fit"), 28.305367),
    # (("Back Together Again", "Roberta Flack"),
    #  ("Back Together Again", "Roberta Flack With Donny Hathaway"), 21.180351),
    # (("Back Together Again", "Roberta Flack And Donny Hathaway"),
    #  ("Back Together Again", "Roberta Flack With Donny Hathaway"), 26.468578),
    # (("Backseat", "New Boyz Ft The Cataracs & Dev"),
    #  ("Backseat", "New Boyz Featuring The Cataracs & Dev"), 24.43826)
]

if __name__ == '__main__':
    unittest.main()
