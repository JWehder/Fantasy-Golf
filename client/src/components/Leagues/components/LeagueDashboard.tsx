import React, { useEffect } from 'react';
import Roster from '../../Teams/components/Roster';
import { useState } from 'react';
import Leaderboard from '../../Tournaments/components/Leaderboard';
import Golfers from '../../Golfers/components/Golfers';
import SquigglyUnderline from "../../Utils/components/SquigglyLine"
import Schedule from '../../Periods/components/Schedule';
import { useDispatch, useSelector } from 'react-redux';
import { useParams, useNavigate, useLocation } from 'react-router-dom';
import Button from '../../Utils/components/Button';
import BackButton from '../../Utils/components/BackButton';
import NextButton from '../../Utils/components/NextButton';
import { AppDispatch, RootState } from '../../../store';
import Modal from '../../Utils/components/Modal';
import { resetSelectedGolfer } from '../../Golfers/state/golferSlice';
import { useQueryClient } from '@tanstack/react-query';
import PlayerPage from '../../Golfers/components/player/PlayerPage';
import NewStandings from "./NewStandings"
import { setSelectedTeam } from '../../Teams/state/teamsSlice';
import { Team } from '../../../types/teams';
import { useFetchUpcomingPeriods } from '../../../hooks/periods';
import { setActiveComponent, getLeague, goToNextSeason } from '../state/leagueSlice';
import LoadingScreen from '../../Utils/components/LoadingScreen';
import { setSelectedGolfer } from '../../Golfers/state/golferSlice';
import { useFetchAvailableGolfers } from '../../../hooks/golfers';
import NotificationBanner from '../../Utils/components/NotificationBanner';

export default function LeagueDashboard() {
    const dispatch = useDispatch<AppDispatch>();
    const { leagueId } = useParams<string>();
    const queryClient = useQueryClient();
    const navigate = useNavigate();
    const location = useLocation();

    const [userSelectedTeam, setUserSelectedTeam] = useState<Team | null>(null);
    const selectedGolfer = useSelector((state: RootState) => state.golfers.selectedGolfer);
    const selectedLeague = useSelector((state: RootState) => state.leagues.selectedLeague);

    const user = useSelector((state: RootState) => state.users.user);
    const leagueTeams = useSelector((state: RootState) => state.teams.leaguesTeams);
    const userTeam = useSelector((state: RootState) => state.teams.userSelectedTeam);
    const activeComponent = useSelector((state: RootState) => state.leagues.activeComponent);
    const goToNextSeasonError = useSelector((state: RootState) => state.leagues.goToNextSeasonError);

    const onClose = () => {
        dispatch(resetSelectedGolfer());
        queryClient.invalidateQueries({ queryKey: ['golferTournamentDetails'] });
    };

    useEffect(() => {
        if (leagueId && !leagueTeams.length) {
            dispatch(getLeague(leagueId));
        };

    }, [leagueId]);

    useEffect(() => {
        if (leagueTeams) {
            dispatch(setSelectedTeam(leagueId));
        };
    }, [leagueTeams, user]);

    const goToSettings = () => {
        navigate(`${location.pathname}/settings`);
    };

    // Fetch upcoming periods
    const {
        data: periodsData,
        fetchNextPage: fetchNextPeriodPage,
        hasNextPage: hasNextPeriodPage,
        isFetchingNextPage: isFetchingNextPeriodPage,
        isError: isPeriodError,
        error: periodError,
    } = useFetchUpcomingPeriods(leagueId!);

    // Fetch available golfers
    const {
        data: golfersData,
        fetchNextPage: fetchNextGolferPage,
        hasNextPage: hasNextGolferPage,
        isFetchingNextPage: isFetchingNextGolferPage,
        isFetching: isFetchingGolfers,
        isError: isGolferError,
        error: golferError,
    } = useFetchAvailableGolfers(leagueId!);

    if (!selectedLeague) {
        return <LoadingScreen />
    };
  
    const handleGolferClick = (golfer: object) => {
      dispatch(setSelectedGolfer(golfer));
    };
  
    const onAddClick = (golferId: string) => {
      console.log(golferId);
    };

    const goToNextSeasonClick = async () => {
        if (leagueId) {
            try {
                // Await the dispatch call to complete
                const resultAction = await dispatch(goToNextSeason(leagueId));
    
                // Check if the action was fulfilled
                if (goToNextSeason.fulfilled.match(resultAction)) {
                    // Append "/settings" to the current path only on success
                    navigate(`${location.pathname}/settings`);
                } else if (goToNextSeason.rejected.match(resultAction)) {
                    // Handle errors (e.g., show a toast notification or log it)
                    console.error("Failed to go to the next season:", resultAction.payload);
                }
            } catch (error) {
                console.error("An unexpected error occurred:", error);
            }
        }
    };

    // Map React Query data to match the expected prop structure
    const golfersPages = golfersData?.pages.map((page) => ({
        golfers: page.golfers,
        nextPage: page.nextPage,
    }));

    const headers = ["Fedex Rank", "Golfer", "Avg Score", "Top 10s", "Wins", "Cuts Made", "Fedex Pts"];

    return (
        <div className='flex justify-center items-center w-full flex-col min-w-[950px] bg-dark max-h-[calc(100vh-100px)]'>

            { goToNextSeasonError ?
            <NotificationBanner
            message={goToNextSeasonError}
            variant="error"
            timeout={10}
            onClose={null}
            />
            :
            ""      
            }

            <div className='flex-row h-16 w-11/12 mb-5 flex items-center text-light font-PTSans min-w-[850px]'>
                <div className='flex flex-col w-1/3'>
                    <div className='flex justify-center items-center flex-row'>
                        <h1 className='text-xl lg:text-4xl md:text-2xl sm:text-xl'>
                            {selectedLeague?.Name}
                        </h1>
                    </div>

                    <div className='flex justify-center items-center flex-row'>
                        <BackButton 
                        size={4}
                        color={"stroke-light"} 
                        handleBackClick={() => console.log("Clicked me")}
                        />
                        <NextButton 
                        size={4}
                        color={"stroke-light"} 
                        handleNextClick={() => console.log("Clicked me")}
                        />
                    </div>
                </div>

                <div className='p-5 flex items-center justify-center w-1/3'>
                        <SquigglyUnderline 
                        items={[{name:"Schedule"}, {name: "Standings"}, {name:"Team"}, {name:"Tournaments"}, {name:"Golfers"}]}
                        setActiveComponent={(e) => dispatch(setActiveComponent(e))}
                        active={activeComponent}
                        />
                </div>

                <div className='w-1/3 flex justify-center items-center'>
                    <Button
                    variant="secondary"
                    type="null"
                    disabled={false}
                    size="md"
                    onClick={goToSettings}
                    >
                        Settings
                    </Button>
                </div>
            </div>
            { selectedLeague.IsCommish && !selectedLeague.ActiveFantasySeason && selectedLeague.CanRenew ?
            (
                <div className='w-full flex justify-center items-center space-x-2 bg-grass-gradient p-4 mb-2'>
                    <span className='font-PTSans text-light'>
                        Your season is over 😕 
                    </span>

                    <Button
                        variant="secondary"
                        type="null"
                        disabled={false}
                        size="md"
                        onClick={goToNextSeasonClick}
                        >
                            Play again?
                    </Button>
                </div>
            )
            :
            ""
            }
            <div className='w-10/12 rounded-lg spy-3 flex-grow shrink flex-row h-full max-h-[calc(100vh-225px)] overflow-auto bg-grass-gradient'> 
                { activeComponent === "Standings" && 
                    <NewStandings 
                    changeUserSelectedTeam={(team: Team) => {
                        setUserSelectedTeam(team);
                        setActiveComponent("Team");
                    }}
                    />
                }
                { activeComponent === "Team" && 
                    <Roster 
                    team={userSelectedTeam || userTeam} 
                    resetUserSelectedTeam={() => setUserSelectedTeam(null)} 
                    userSelectedTeam={!!userSelectedTeam}
                    />
                } 
                { activeComponent === "Tournaments" && 
                    <Leaderboard />
                }
                { activeComponent === "Golfers" && 
                    <Golfers
                    headers={headers}
                    data={golfersPages || []}
                    isFetching={isFetchingGolfers}
                    isFetchingNextPage={isFetchingNextGolferPage}
                    hasNextPage={hasNextGolferPage}
                    fetchNextPage={fetchNextGolferPage}
                    onGolferClick={handleGolferClick}
                    onAddClick={onAddClick}
                    />
                }
                { activeComponent === "Schedule" && 
                    <Schedule
                    data={periodsData}
                    fetchNextPage={fetchNextPeriodPage}
                    hasNextPage={hasNextPeriodPage}
                    isFetchingNextPage={isFetchingNextPeriodPage}
                    isError={isPeriodError}
                    error={periodError}
                    />
                }
            </div>
            
            { selectedGolfer ?
                <Modal 
                open={open} 
                onClose={onClose} 
                bgColor="dark-green"
                closeButtonColor={'light'}
                >
                <div className="w-full h-auto flex items-center justify-center min-w-[900px]">
                    <div className="w-[90%] p-4 bg-middle rounded-xl transition-all duration-300 ease-in-out">
                        <PlayerPage />
                    </div>
                </div>
                </Modal>
                :
                ""
            }

        </div>
    );
  }