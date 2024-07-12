document.addEventListener("DOMContentLoaded", function() {
    const matches = [
        { player1: null, player2: null, winner: null },
        { player1: null, player2: null, winner: null },
        { player1: null, player2: null, winner: null },
        { player1: null, player2: null, winner: null }
    ];

    const player1 = document.getElementById("player1-1");
    const player2 = document.getElementById("player1-2");

    async function fetchCurrentUser() {
        // Fetch the current logged-in user's username
        const response = await fetch('/api/get_tournament_players/');
        const data = await response.json();
        return data.username;
    }

    async function registerPlayer() {
        const username = await fetchCurrentUser();
        // Register the player in the tournament bracket
        if (username) {
            for (let i = 0; i < matches.length; i++) {
                if (!matches[i].player1) {
                    matches[i].player1 = username;
                    break;
                } else if (!matches[i].player2) {
                    matches[i].player2 = username;
                    break;
                }
            }
            console.log(matches);
            updateBracket();
        }
    }

    function updateBracket() {
       player1.innerText = matches[0].player1;
       player2.innerText = matches[0].player2;
    }

    // function updateBracket() {
    //     for (let i = 0; i < matches.length; i++) {
    //         if (matches[i].player1) {
    //             document.getElementById(`player1-${i + 1}`).innerText = matches[i].player1;
    //         }
    //         if (matches[i].player2) {
    //             document.getElementById(`player1-${i + 2}`).innerText = matches[i].player2;
    //         }
    //     }
    // }



    // Register the player and update the bracket on page load
    registerPlayer();

    // Attach event listeners
    //document.getElementById("start-tournament").addEventListener("click", startTournament);
});
