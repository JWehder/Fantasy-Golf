export interface LeagueSettings {
    _id?: string;  // PyObjectId to string
    created_at?: string;  // datetime to string
    CutPenalty: number;  // integer type
    DraftingFrequency: number;
    DraftStartDayOfWeek?: string;
    DraftStartTime?: string;
    DraftType: string;
    DropDeadline?: string;
    ForceDrops?: number;
    HeadToHead: boolean;
    LeagueId: string;  // PyObjectId to string
    MaxDraftedPlayers: number;
    MaxGolfersPerTeam: number;
    MaxNumOfGolferUses?: number;
    MinFreeAgentDraftRounds: number;
    NumOfBenchGolfers: number;
    NumOfStarters: number;
    NumberOfTeams?: number;
    PointsPerPlacing?: number[];  // List[int] to number array
    PointsPerScore: {  // dictionary type
      Birdies?: number;
      Eagles?: number;
      Pars?: number;
      Albatross?: number;
      Bogeys?: number;
      DoubleBogeys?: number;
      WorseThanDoubleBogeys?: number;
    };
    Game: "Standard" | "Head to Head" | "Match Play";
    PointsType: "Strokes" | "Points per Score" | "Matchup Win";
    SecondsPerDraftPick?: number;
    TimeZone: string;
    updated_at?: string;  // datetime to string
    WaiverDeadline?: string;
    WaiverType: string;
    DefaultPointsForNonPlacers: number;
    Sport: string;
    ProSeasonId: string;
    ProSeason: string;
    IsCommish: boolean;
  }