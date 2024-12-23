import { DraftPick } from "./draftPicks";

export interface Draft {
    id: string;
    LeagueId: string;
    StartDate: Date;
    EndDate: Date;
    Rounds: number;
    PeriodId: string;
    DraftPicks: Array[DraftPick]
    DraftOrder: Array[string];
    IsComplete: boolean;
    created_at: Date
    updated_at: Date
}