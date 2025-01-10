import { Team } from "./teams"
import { LeagueSettings } from "./leagueSettings"

interface League {
    id: string;
    Name: string;
    CommissionerId?: string;
    Game: string;
    Teams?: Team[];
    LeagueSettings: LeagueSettings;
    FantasyLeagueSeasons?: string[];
    CurrentFantasyLeagueSeasonId?: string;
    WaiverOrder?: string[];
    created_at?: string;
    updated_at?: string;
    IsCommish?: boolean;
    ActiveFantasySeason?: boolean;
    CanRenew: boolean;
}