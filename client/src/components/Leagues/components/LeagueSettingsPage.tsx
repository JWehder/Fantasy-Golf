import React, { useEffect, useState, useMemo, ReactNode } from "react";
import { useDispatch, useSelector } from "react-redux";
import { AppDispatch, RootState } from "../../../store";
import { getLeague, updateLeagueSettings } from "../state/leagueSlice";
import { useParams, useNavigate } from "react-router-dom";
import { LeagueSettings } from "../../../types/leagueSettings";
import TournamentScheduleTable from "../../Tournaments/components/TournamentScheduleTable";
import { Tournament } from "../../../types/tournaments";
import Tourney from "../../Tournaments/components/Tourney";
import BackButton from "../../Utils/components/BackButton";
import GolferTournamentDetailsTable from "../../Tournaments/components/GolferTournamentDetailsTable";
import { SettingsProvider } from "../settingsContext";
import LoadingScreen from "../../Utils/components/LoadingScreen";
import axios from "axios";
import EditTournamentsButtons from "./EditTournamentsButtons";
import { FantasyLeagueTournamentsResponse } from "../../../types/fantasyLeagueTournamentsResponse";
import TimeZoneSelector from "./TimeZoneSelector";

interface PointsPerScoreArgs {
  name: string;
  subname: string;
}

const LeagueSettingsPage: React.FC = () => {
  const navigate = useNavigate();
  const { leagueId } = useParams<string>();
  const isEditMode = Boolean(leagueId);

  const [currentTab, setCurrentTab] = useState<string>("General");
  const [settings, setSettings] = useState<LeagueSettings | undefined>();
  const [errors, setErrors] = useState<{ [key: string]: string }>({});
  const selectedLeague = useSelector((state: RootState) => state.leagues.selectedLeague);
  const [selectedTournament, setSelectedTournament] = useState<Tournament | null>(null);
  const [tournaments, setTournaments] = useState<FantasyLeagueTournamentsResponse | Tournament[]>();

  const dispatch = useDispatch<AppDispatch>();

  const defaultPointsPerScore = {
    'Albatross': 7,
    'Eagles': 5,
    'Birdies': 3,
    'Pars': 1,
    'Bogeys': -1,
    'DoubleBogeys': -3,
    'WorseThanDoubleBogeys': -5,
  };

  useEffect(() => {
      if (isEditMode && !selectedLeague) {
        dispatch(getLeague(leagueId!));
      }
    }, [leagueId, isEditMode, dispatch, selectedLeague]);
    
    useEffect(() => {
      if (isEditMode && selectedLeague) {
        setSettings(selectedLeague.LeagueSettings);
    
        // Fetch associated tournaments
        const fetchTournaments = async () => {
          try {
            const response = await axios.get(
              `/api/fantasy_league_seasons/${selectedLeague.CurrentFantasyLeagueSeasonId}/pro_season/competition_schedule`
            );
            console.log(response.data)
            setTournaments(response.data); // Assuming `setTournaments` exists for tournament state
          } catch (error) {
            console.error("Error fetching tournaments:", error);
          }
        };
        fetchTournaments();
      } 
    }, [isEditMode, selectedLeague]);
    
    useEffect(() => {
      const fetchData = async () => {
        try {
          let settingsResponse = isEditMode
            ? selectedLeague?.LeagueSettings
            : await axios.get('/default_league_settings').then((res) => res.data);
    
          const tournamentsResponse = await axios.get(
            isEditMode
              ? `/api/fantasy_league_seasons/${selectedLeague?.CurrentFantasyLeagueSeasonId}/pro_season/competition_schedule`
              : `/api/pro_seasons/${settingsResponse.ProSeasonId}/competition_schedule`
          );

          let newSettingsResponse = { ...settingsResponse }
          
          // Apply default PointsPerScore if undefined or empty
          if (!settingsResponse?.PointsPerScore || Object.keys(settingsResponse.PointsPerScore).length === 0) {
            newSettingsResponse.PointsPerScore = defaultPointsPerScore
          }
          setSettings(newSettingsResponse);
          setTournaments(tournamentsResponse.data);
        } catch (error) {
          console.error("Error fetching data:", error);
        }
      };
    
      fetchData();
    }, [isEditMode, selectedLeague]);

  const handleInputChange = (field: keyof LeagueSettings | PointsPerScoreArgs, value: any) => {
    if (!settings) return;

    // Validation logic
    let errorMessage = "";
    if (field === "NumOfStarters" && value > settings.MaxGolfersPerTeam) {
      errorMessage = "Number of starters cannot exceed max golfers per team.";
    } else if (field === "NumOfBenchGolfers" && value > settings.MaxGolfersPerTeam) {
        errorMessage = "Number of bench golfers cannot exceed max golfers per team.";
    } else if (field === "NumberOfTeams" && value % 2 !== 0 && settings.Game === "Match Play") {
        errorMessage
    }

    if(typeof field === "object" && field.name === "PointsPerScore") {
      setSettings((prev) => {
        if (!prev) return undefined; // Handle undefined previous state
        
        return {
          ...prev,
          PointsPerScore: {
            ...prev.PointsPerScore,
            [field.subname]: value, // Update the specific score
          },
        };
      });
      

    } else {
      // Set error if validation fails
      if (errorMessage) {
        setErrors((prev) => ({ ...prev, [field as keyof LeagueSettings]: errorMessage }));
        return;
      }

      // Clear error for valid input and update state
      setErrors((prev) => ({ ...prev, [field as keyof LeagueSettings]: "" }));
      setSettings((prev) => ({ ...prev!, [field as keyof LeagueSettings]: value }));
    }
  };

  const handleSave = () => {
      if (isEditMode && settings) dispatch(updateLeagueSettings({ leagueSettings: settings }));
      else if (!isEditMode && settings) null;
  };

  const timePerDraftPickObj = {
      "30 secs": 30, 
      "1 min": 60, 
      "1 min 30 secs": 90, 
      "2 mins": 120, 
      "1 hour": 3600, 
      "3 hours": 10800, 
      "6 hours": 21600
  }

  const cutsObj = {
      "+1": 1,
      "+2": 2,
      "+3": 3,
      "+4": 4
  };

  const displayStarters = useMemo(() => {
    const maxGolfers = settings?.MaxGolfersPerTeam ?? 0;
    const numBench = settings?.NumOfBenchGolfers ?? 0;
  
    return Array.from(
      { length: Math.max(0, maxGolfers - numBench - 2 + 1) },
      (_, i) => i + 2
    );
  }, [settings]);

  const renderSurroundingPoints = (field: keyof typeof defaultPointsPerScore) => {
    return [defaultPointsPerScore[field] - 2, 
    defaultPointsPerScore[field] - 1, defaultPointsPerScore[field], defaultPointsPerScore[field] + 1, defaultPointsPerScore[field] + 2];
  };
  
  const displayBenchGolfers = useMemo(() => {
    const maxGolfers = settings?.MaxGolfersPerTeam ?? 0;
    const numStarters = settings?.NumOfStarters ?? 0;
  
    return Array.from(
      { length: Math.max(0, maxGolfers - numStarters - 1 + 1) },
      (_, i) => i + 1
    );
  }, [settings]);

  const renderInput = (
    label: string, key: keyof LeagueSettings | PointsPerScoreArgs, type: string, value: any, options: Array<string> | Array<number> | null, disabled = false, obj: Record<string, number> | undefined = undefined) => {

      if (options) {
        return (
          <div className="space-y-2">
            <label className="text-sm font-semibold">{label}</label>
            <div className="flex flex-wrap gap-2">
              {options.map((option) => ( 
                <button
                  key={option}
                  onClick={() => handleInputChange(key, (obj ? obj[option] : option))}
                  className={`px-4 py-2 rounded ${
                    value === (obj ? obj[option] : option) ? "bg-highlightBlue text-light" : "bg-light text-dark"
                  } ${disabled ? "cursor-not-allowed opacity-50" : "hover:brightness-110"}`}
                  disabled={disabled}
                >
                  {option}
                </button>
              ))}
            </div>
          </div>
        );
      }
  
      return (
        <div className="space-y-2 flex flex-col">
          <label className="text-sm font-semibold">{label}</label>
          <div className="flex flex-row">
            <input
              type={type}
              value={value}
              onChange={(e) => handleInputChange(key, type === "number" ? parseInt(e.target.value) : e.target.value)}
              className="max-w-36 p-2 rounded bg-light text-dark focus:ring focus:ring-highlightBlue mr-2"
              disabled={disabled}
            />
          </div>
        </div>
      );
  };

  if (!settings) {
      return <LoadingScreen />
  };

  return (
  <div className="w-full min-h-screen bg-gradient-to-b from-dark to-middle text-light flex flex-col items-center font-PTSans p-3 min-w-[570px]">
      <div className="w-full max-w-4xl bg-middle p-6 rounded-lg shadow-xl font-PTSans items-center">

      <div className='w-full flex justify-center items-center space-x-2 bg-grass-gradient p-4'>
        <span className='font-PTSans text-light'>
            New season has been created. Please add tournaments. 
        </span>
      </div>

      <div className="flex flex-row items-center p-4 w-full">
        <div className="flex justify-start w-1/3">
          <BackButton
            size={8}
            color="stroke-light"
            handleBackClick={() => navigate(`/leagues/${leagueId}`)}
          />
        </div>
        <div className="flex justify-center w-1/3">
          <h1 className="text-2xl sm:text-xl md:text-xl lg:text-2xl font-bold text-center text-light">
            league settings
          </h1>
        </div>
        <div className="w-1/3"></div>
      </div>


        {/* Tabs for Navigation */}
        <div className="flex justify-center mb-6 text-light space-x-2">
            {["General", "Draft", "Scoring", "Team Management", "Tournaments", "Teams"].map((tab) => (
            <button
                key={tab}
                onClick={() => setCurrentTab(tab)}
                className={`px-4 py-2 rounded-t-lg text-sm sm:text-xs md:text-sm lg:text-sm  ${
                currentTab === tab ? "bg-dark text-light" : "bg-light text-dark hover:brightness-125"
                }`}
            >
                {tab} ❗ 
            </button>
            ))}
        </div>

        {/* Content */}
        {currentTab === "General" && (
            <div className="space-y-6 min-w-[700px]">
                {renderInput(
                "Sport",
                "Sport",
                "text",
                settings?.Sport,
                ["Golf"],
                !selectedLeague?.IsCommish
                )}
                { renderInput(
                "Pro Season",
                "ProSeason",
                "number",
                settings?.ProSeason,
                ["PGA Tour"],
                !selectedLeague?.IsCommish
                )}
                {renderInput("Number of Teams", "NumberOfTeams", "number", settings?.NumberOfTeams, [8, 9, 10, 12, 14, 16], !selectedLeague?.IsCommish)}
            </div>
        )}

        {/* Content */}
        {currentTab === "Draft" && (
            <div className="space-y-6">
                {renderInput(
                "Draft Frequency (Free Agent Draft every X amount of tournaments after first draft)",
                "DraftingFrequency",
                "number",
                settings?.DraftingFrequency,
                [1, 2, 3, 4],
                !selectedLeague?.IsCommish
                )}
                {renderInput(
                "Draft Start Day",
                "DraftStartDayOfWeek",
                "text",
                settings?.DraftStartDayOfWeek,
                ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
                !selectedLeague?.IsCommish
                )}
                {renderInput(
                "Time Per Draft Pick",
                "SecondsPerDraftPick",
                "text",
                settings?.SecondsPerDraftPick,
                Object.keys(timePerDraftPickObj),
                !selectedLeague?.IsCommish,
                timePerDraftPickObj
                )}
                {renderInput("Draft Time", "DraftStartTime", "time", settings?.DraftStartTime, null, !selectedLeague?.IsCommish)}
                <TimeZoneSelector
                onChange={(zone) => handleInputChange("TimeZone", zone)}
                value={settings?.TimeZone}
                disabled={!selectedLeague?.IsCommish}
                />
                {renderInput("Draft Type", "DraftType", "text", settings?.DraftType, ["Snake Draft", "Standard"], !selectedLeague?.IsCommish)}
            </div>
            )}

            {currentTab === "Scoring" && (
            <div className="space-y-6 flex flex-col">
              {renderInput(
              "Points Type",
              "PointsType",
              "text",
              settings?.PointsType,
              ["Strokes", "Points per Score", "Matchup Win"],
              !selectedLeague?.IsCommish
              )}
              {settings?.PointsType === "Points per Score" &&
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
                  {Object.keys(settings?.PointsPerScore || {}).map((scoreType: string) =>
                    renderInput(
                      `Points for ${scoreType}`,
                      {name: 'PointsPerScore', subname: scoreType},
                      "number",
                      settings?.PointsPerScore[scoreType as keyof typeof settings.PointsPerScore],
                      renderSurroundingPoints(scoreType as keyof typeof defaultPointsPerScore)
                      ,
                      !selectedLeague?.IsCommish
                    )
                  )}
                </div>
                }
                {renderInput("Game", "Game", "text", settings?.Game, ["Match Play", "Standard", "Head to Head"], !selectedLeague?.IsCommish)}
                {renderInput("Default Points for Non-Placers (How many points a player who withdrawals receives)", "DefaultPointsForNonPlacers", "number", settings?.DefaultPointsForNonPlacers, [0, 1, 2, 3, 4], !selectedLeague?.IsCommish)}
                {renderInput("Cut Penalty", "CutPenalty", "text", settings?.CutPenalty, Object.keys(cutsObj), !selectedLeague?.IsCommish, cutsObj)}
            </div>
            )}

            {currentTab === "Team Management" && (
            <div className="space-y-6 ">
                {renderInput("Cut Penalty (Strokes added for missing the cut)", "CutPenalty", "number", settings?.CutPenalty, [0, 1, 2, 3], !selectedLeague?.IsCommish)}
                {renderInput("Number of Bench Golfers", "NumOfBenchGolfers", "number", settings?.NumOfBenchGolfers, displayBenchGolfers, !selectedLeague?.IsCommish)}
                {renderInput("Number of Starters", "NumOfStarters", "number", settings?.NumOfStarters, displayStarters, !selectedLeague?.IsCommish)}
                {renderInput("Force Drops", 
                "ForceDrops", 
                "number", 
                settings?.ForceDrops, 
                Array.from(
                    { length: Math.max(0, settings!.MaxGolfersPerTeam - 1 + 1) }, 
                    (_, i) => i 
                ), 
                !selectedLeague?.IsCommish)}
                {renderInput("Max Golfers Per Team", "MaxGolfersPerTeam", "number", settings?.MaxGolfersPerTeam, [2, 3, 4, 5, 6], !selectedLeague?.IsCommish)}
                {renderInput(
                "Waiver Type",
                "WaiverType",
                "text",
                settings?.WaiverType,
                ["Reverse Standings", "Rolling Waivers"],
                !selectedLeague?.IsCommish
                )}

                {renderInput(
                "Waiver Deadline",
                "WaiverDeadline",
                "text",
                settings?.WaiverDeadline,
                ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
                !selectedLeague?.IsCommish
                )}
            </div>
            )}

            {currentTab === "Tournaments" && tournaments &&
            (
                
                selectedTournament ? (
                <>
                    <span className="inline-flex items-center">
                    <BackButton
                        size={8}
                        color="stroke-light"
                        handleBackClick={() => setSelectedTournament(null)}
                    />
                    </span>
                    <Tourney tournament={selectedTournament} />
                    <GolferTournamentDetailsTable
                    tournamentId={selectedTournament.id}
                    holeData={selectedTournament.Holes}
                    />
                </>
                ) : (
                tournaments ?
                <>
                    <SettingsProvider>
                        { !isEditMode ?
                          <TournamentScheduleTable
                          tournaments={tournaments as Tournament[]}
                          />
                          :
                          <EditTournamentsButtons 
                          setTournaments={setTournaments}
                          fantasyLeagueSeasonId={selectedLeague?.CurrentFantasyLeagueSeasonId!}
                          />
                        }

                        {
                          tournaments && 
                          typeof tournaments === "object" && 
                          "pastFantasyLeagueTournaments" in tournaments &&
                          tournaments?.pastFantasyLeagueTournaments.length > 0 && (
                            // Render your tournamentScheduleTable here
                            <>
                              <h1 className="text-2xl font-bold p-4 text-center text-light">
                                past fantasy league events
                              </h1>
                              <TournamentScheduleTable 
                              tournaments={tournaments?.pastFantasyLeagueTournaments}
                              />
                            </>
                          )
                        }
                        {
                          tournaments && 
                          typeof tournaments === "object" && 
                          "upcomingFantasyLeagueTournaments" in tournaments &&
                          tournaments?.upcomingFantasyLeagueTournaments.length > 0 && (
                            // Render your tournamentScheduleTable here
                            <>
                              <h1 className="text-2xl font-bold p-4 text-center text-light">
                                upcoming fantasy league events
                              </h1>
                              
                              <TournamentScheduleTable 
                              tournaments={tournaments?.upcomingFantasyLeagueTournaments}
                              />
                            </>
                          )
                        }
                        {
                          tournaments && 
                          typeof tournaments === "object" && 
                          "upcomingProSeasonTournaments" in tournaments &&
                          tournaments?.upcomingProSeasonTournaments.length > 0 && (
                            // Render your tournamentScheduleTable here
                            <>
                              <h1 className="text-2xl font-bold p-4 text-center text-light">
                                upcoming pro events
                              </h1>
                              <TournamentScheduleTable 
                              tournaments={tournaments?.upcomingProSeasonTournaments}
                              />
                            </>

                          )
                        }

                    </SettingsProvider>
                </>
                :
                <LoadingScreen />
                )
            )}
        </div>


        {/* Save Button */}
        <div className="flex justify-center mt-6">
            <button
            onClick={handleSave}
            className={`bg-light text-dark px-6 py-3 rounded-lg shadow-2xl
            ${!selectedLeague?.IsCommish ? "cursor-not-allowed opacity-50" : "hover:brightness-110"}
            `}
            disabled={!selectedLeague?.IsCommish}
            >
            Save Settings
            </button>
        </div>
      </div>
  );
};

export default LeagueSettingsPage;
