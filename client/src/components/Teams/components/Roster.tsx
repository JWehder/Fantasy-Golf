import PlayerData from "../../Golfers/components/PlayerData";
import Headers from "../../Utils/components/TableHeaders";
import DashboardTitle from "../../User/components/home/DashboardTitle";
import Button from "../../Utils/components/Button";
import React from "react";
import { Golfer } from "../../../types/golfers";
import { Team } from "../../../types/teams";
import { useDispatch } from "react-redux";
import { AppDispatch } from "../../../store";
import { setSelectedGolfer } from "../../Golfers/state/golferSlice";
import BackButton from "../../Utils/components/BackButton";
import Avatar from "../../Utils/components/Avatar";

export default function Roster({ 
    team, resetUserSelectedTeam, userSelectedTeam } : 
    { 
    team: Team | null, 
    resetUserSelectedTeam: () => void,
    userSelectedTeam: boolean
    }) {

    
    const dispatch = useDispatch<AppDispatch>();

    const handleGolferClick = (golfer: object) => {
        dispatch(setSelectedGolfer(golfer));
    };
    
    const displayRoster = team?.Golfers.map((player: Golfer, idx) => {
        return <PlayerData
        player={player}
        even={idx % 2 === 0}
        onClick={() => handleGolferClick(player)}
        />
    })

    function handleBackButtonClick() {
        resetUserSelectedTeam();
    };

    const headers = ["Rank", "Golfer", "Avg Score", "Top 10s", "Wins", "Cuts Made", "Fedex Pts"]

    return (
        <div className="w-full bg-dark text-light flex flex-col items-center font-PTSans">
            <div className="w-full max-w-5xl bg-middle my-4 p-4 rounded-md shadow-lg">
                { userSelectedTeam ?
                    <>
                        {/* Back Button */}
                        <span className='inline-flex items-center'>
                            <BackButton 
                                size={8}
                                color={"stroke-light"} 
                                handleBackClick={() => handleBackButtonClick()}
                            />
                        </span>
                    </>
                    :
                    null
                }
                <DashboardTitle 
                title={`${team?.TeamName} - ${team?.Placement}`}
                avatar={'nothing'}
                >

                    <div className="flex-1 flex items-center justify-center">
                        <div className="mr-2">
                            <Button 
                                variant="secondary" 
                                size="md"
                                disabled={false}
                                onClick={null}
                                type={null}
                            >
                                Trade
                            </Button>
                        </div>


                        <Button 
                            variant="secondary" 
                            size="md"
                            disabled={false}
                            onClick={null}
                            type={null}
                        >
                            Waivers
                        </Button>
                    </div>
                </DashboardTitle>
                <Headers headers={headers} />
                {displayRoster}

            </div>

        </div>
    )
}