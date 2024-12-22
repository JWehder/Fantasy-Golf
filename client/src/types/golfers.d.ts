export interface Golfer {
    id: string;  // String instead of ObjectId since it comes from API
    Rank?: number;
    FirstName: string;
    LastName: string;
    Age?: number;
    Country?: string;
    Earnings?: number;
    FedexPts?: number;
    Events?: number;
    Rounds?: number;
    Flag?: string;
    Cuts?: number;
    Top10s?: number;
    Wins?: number;
    AvgScore?: number;
    GolferPageLink?: string;
    Birthdate?: Date;
    Birthplace?: string;
    HtWt?: string;
    College?: string;
    Swing?: string;
    TurnedPro?: string;
    OWGR?: number | undefined;
    created_at?: Date;
    updated_at?: Date;
}