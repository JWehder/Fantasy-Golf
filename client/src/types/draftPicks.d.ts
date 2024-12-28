import { Golfer } from "./golfers";

export interface DraftPick {
    id: string;
    TeamId: string;
    GolferId: string;
    RoundNumber: number;
    PickNumber: number;
    LeagueId: string;
    DraftId: string;
    Golfer: Golfer;
    created_at: Date;
    updated_at: Date;
}