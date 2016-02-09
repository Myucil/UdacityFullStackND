import fresh_tomatoes
import media

coffee_and_cigarettes = media.Movie("Coffee and Cigarettes",
                        "A series of short films by Jim Jarmusch, all featuring coffee and cigarettes",
                        "https://upload.wikimedia.org/wikipedia/en/8/8d/Coffee_and_Cigarettes_movie.jpg",
                        "https://www.youtube.com/watch?v=mM6Mpn0-eyQ", "Jim Jarmusch", "http://www.imdb.com/title/tt0379217/?ref_=nv_sr_1")

strangers_on_a_train = media.Movie("Strangers on a Train",
                     "Two men meet on a train and decide to swap murders",
                     "https://upload.wikimedia.org/wikipedia/commons/e/ec/Strangers_on_a_Train_title_shot.png",
                     "https://www.youtube.com/watch?v=J1iSS5r0OVE", "Alfred Hitchcock","http://www.imdb.com/title/tt0044079/?ref_=nv_sr_1")
                     
ulysses_gaze = media.Movie("Ulysses' Gaze",
                           "A man travels through eastern Europe in pursuit of a lost film, an odyssey into the region's history, past and present",
                           "https://upload.wikimedia.org/wikipedia/en/b/bc/Ulysses%27_Gaze_Poster.jpg",
                           "https://www.youtube.com/watch?v=DaUEulIEBV8", "Theodoros Angelopoulos","http://www.imdb.com/title/tt0114863/?ref_=fn_al_tt_1")

fight_club = media.Movie("Fight Club",
                         "A man meets his extreme alter ego, starting a fight club and a revolution",
                         "https://upload.wikimedia.org/wikipedia/en/f/fc/Fight_Club_poster.jpg", 
                         "https://www.youtube.com/watch?v=SUXWAEX2jlg", "David Fincher", "http://www.imdb.com/title/tt0137523/?ref_=nv_sr_1")

bleu = media.Movie("Trois Couleurs: Bleu",
                   "A woman loses her child and husband in an accident and finds her self in a strange kind of freedom",
                   "https://upload.wikimedia.org/wikipedia/en/2/2c/Bluevidcov.jpg",
                   "https://www.youtube.com/watch?v=Hxu6my_t4pM", "Krysztof Kieslowski", "http://www.imdb.com/title/tt0108394/?ref_=nv_sr_2")

lotr = media.Movie("The Lord of the Rings: The Fellowship of the Ring",
                   "A hobbit becomes the unlikely hero in a quest to defeat ultimate evil",
                   "https://upload.wikimedia.org/wikipedia/en/0/0c/The_Fellowship_Of_The_Ring.jpg",
                   "https://www.youtube.com/watch?v=V75dMMIW2B4", "Peter Jackson", "http://www.imdb.com/title/tt0120737/?ref_=nv_sr_1")

movies = [coffee_and_cigarettes, strangers_on_a_train, ulysses_gaze, fight_club, bleu, lotr]
fresh_tomatoes.open_movies_page(movies)


