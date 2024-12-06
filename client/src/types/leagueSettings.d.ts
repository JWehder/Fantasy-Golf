export interface LeagueSettings {
    id?: string;  // PyObjectId to string
    created_at?: string;  // datetime to string
    CutPenalty: number;  // integer type
    DraftingFrequency: number;
    DraftStartDayOfWeek?: string;
    DraftStartTime?: string;
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
    PointsPerScore?: {  // dictionary type
      Birdies: number;
      Eagles: number;
      Pars: number;
      Albatross: number;
      Bogeys: number;
      DoubleBogeys: number;
      WorseThanDoubleBogeys: number;
    };
    ScoreType: "Total Standings" | "Head to Head" | "Match Play";
    PointsType: "Strokes" | "Points per Score" | "Matchup Win";
    SecondsPerDraftPick?: number;
    SnakeDraft: boolean;
    StrokePlay: boolean;
    TimeZone: string;
    updated_at?: string;  // datetime to string
    WaiverDeadline?: string;
    WaiverType: string;
    DefaultPointsForNonPlacers: number;
  }