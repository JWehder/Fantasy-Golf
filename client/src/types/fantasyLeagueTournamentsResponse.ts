import { Tournament } from "./tournaments"

export interface FantasyLeagueTournamentsResponse {
    pastFantasyLeagueTournaments?: Array<Tournament>,
    upcomingFantasyLeagueTournaments?: Array<Tournament>,
    upcomingProSeasonTournaments?: Array<Tournament>,
    allTournaments?: Array<Tournament>
}