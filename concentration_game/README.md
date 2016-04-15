#Full Stack Nanodegree Project 4: Concentration Game

## Set-Up Instructions:
1.  Update the value of application in app.yaml to the app ID you have registered
 in the App Engine admin console and would like to use to host your instance of this sample.
1.  Run the app with the devserver using dev_appserver.py DIR, and ensure it's
 running by visiting the API Explorer - by default localhost:8080/_ah/api/explorer.
1.  (Optional) Generate your client library(ies) with the endpoints tool.
 Deploy your application.
 
 
 
##Game Description:
Concentration game, which is also commonly known as card matching game, is a guessing game to match a pair of cards among a set of cards laid face down. Each game begins with a set of cards (often 52 is used as the standard), and a player can pick two cards to flip. If the flipped cards are a pair, then the pair remains face up, but if not, the two cards are flipped back. The game is won when all the cards are guessed correctly and face up. Maximum number of attempts can be set and if the player fails to flip all the cards within the limit, the game will be lost. For this app, only a single player plays the game and tries to reach a good score, which is defined by a ratio of how many attempts are left over how many attempts are allowed. 'Guesses' are sent to the `make_guess` endpoint which will reply with whether the guess was correct or not. If not, the endpoint will tell what the numbers of each cards are. Each game can be retrieved or played by using the path parameter
`urlsafe_game_key`.

##Files Included:
 - api.py: Contains endpoints and game playing logic.
 - app.yaml: App configuration.
 - cron.yaml: Cronjob configuration.
 - main.py: Handler for taskqueue handler.
 - models.py: Entity and message definitions including helper methods.
 - utils.py: Helper function for retrieving ndb.Models by urlsafe Key string and generating random pairs.

##Endpoints Included:
 - **create_user**
    - Path: 'user'
    - Method: POST
    - Parameters: user_name, email (optional)
    - Returns: Message confirming creation of the User.
    - Description: Creates a new User. user_name provided must be unique. Will 
    raise a ConflictException if a User with that user_name already exists.
    
 - **new_game**
    - Path: 'game'
    - Method: POST
    - Parameters: user_name, attempts
    - Returns: GameForm with initial game state.
    - Description: Creates a new Game. user_name provided must correspond to an
    existing user - will raise a NotFoundException if not. Number of attempts cannot be less than number of pairs, which is standard 26 pairs for this app - will raise a BadRequestException.
     
 - **get_game**
    - Path: 'game/{urlsafe_game_key}'
    - Method: GET
    - Parameters: urlsafe_game_key
    - Returns: GameForm with current game state.
    - Description: Returns the current state of a game.
 
 - **get_user_game**
    - Path: 'game/user/{user_name}'
    - Method: GET
    - Parameters: user_name
    - Returns: GameForms with all of games a user has played.
    - Description: Returns all of games a user has played.
 
 - **cancel_game**
    - Path: 'game/{urlsafe_game_key}/cancel'
    - Method: DELETE
    - Parameters: urlsafe_game_key
    - Returns: GameForm with current game state.
    - Description: Cancels the specified game by deleting from the database. Finished game cannot be deleted.
    
 - **make_guess**
    - Path: 'game/{urlsafe_game_key}'
    - Method: PUT
    - Parameters: urlsafe_game_key, guess1, guess2
    - Returns: GameForm with new game state.
    - Description: Accepts two integers 'guess1' and 'guess2' and returns the updated state of the game. The two guesses needs to be different integers, needs to be within 0 and the number of cards, which is 52 for this app, and cannot be previous correct guesses. GameForm will be returned with an error message when these conditions are not met. If this causes a game to end, a corresponding Score and AverageScore entity will be created. Also, saves this guess in a Game's history parameter.
    
 - **get_scores**
    - Path: 'scores'
    - Method: GET
    - Parameters: None
    - Returns: ScoreForms.
    - Description: Returns all Scores in the database (unordered).
    
 - **get_user_scores**
    - Path: 'scores/user/{user_name}'
    - Method: GET
    - Parameters: user_name
    - Returns: ScoreForms. 
    - Description: Returns all Scores recorded by the provided player (unordered).
    Will raise a NotFoundException if the User does not exist.

 - **get_high_scores**
    - Path: 'scores/highest'
    - Method: GET
    - Parameters: number_of_results (optional)
    - Returns: ScoreForms. 
    - Description: Returns highest Scores for games that are won. An optional parameter number_of_results can limit the number of scores returned.
 
 - **get_user_rankings**
    - Path: 'user/{user_name}/rank'
    - Method: GET
    - Parameters: user_name
    - Returns: UserRankingForm.
    - Description: Returns a user's average score and rank.
    
 - **get_game_history**
    - Path: 'games/{urlsafe_game_key}/history'
    - Method: GET
    - Parameters: urlsafe_game_key
    - Returns: GameHistoryForm
    - Description: Gets the history of guesses made for a Game.

##Models Included:
 - **User**
    - Stores unique user_name and (optional) email address.
    
 - **Game**
    - Stores unique game states and guess history. Associated with User model via KeyProperty.
    
 - **Score**
    - Records completed games. Has a property `score` which is used to compare games with different number of attempts. It is calculated by number of remaining gusses divided by total attempts allowed. Associated with Users model via KeyProperty.
    
 - **AverageScore**
    - Records average score of a player. It is used to compare performance of different players.
    
##Forms Included:
 - **GameForm**
    - Representation of a Game's state (urlsafe_key, attempts_remaining,
    game_over flag, message, user_name, card_layout).
 - **GameHistoryForm**
    - Shows history of guesses of a Game (urlsafe_key, history).
 - **NewGameForm**
    - Used to create a new game (user_name, attempts).
 - **MakeGuessForm**
    - Inbound form for making guess for a pair of cards (guess1, guess2).
 - **ScoreForm**
    - Representation of a completed game's Score (user_name, date, won flag,
    guesses, score).
 - **ScoreForms**
    - Multiple ScoreForm container.
 - **UserRankingForm**
    - Shows a user's average score and rank (user_name, rank, score).
 - **StringMessage**
    - General purpose String container.
