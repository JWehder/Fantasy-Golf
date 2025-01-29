import TData from "../../../Utils/components/TData";
import THead from "../../../Utils/components/THead";
import React, { useState, useMemo } from "react";
import { Round } from "../../../../types/rounds";
import { TournamentHoles } from "../../../../types/tournamentHoles";
import { ScoreWrapper } from "./ScoreWrapper";

export default function HolesComparisonChart({ rounds, holes } : { rounds: Round[], holes: TournamentHoles[] }) {
    const [currentRound, setCurrentRound] = useState<number>(0);
    const [showSummary, setShowSummary] = useState<boolean>(true);
    const [selectCurrentRound, setSelectCurrentRound] = useState<number>(rounds.length);

    // Handle cases where rounds data is missing or empty
    if (!rounds || rounds.length === 0) {
        return (
            <div className="w-full h-16 flex justify-center items-center text-center">
                Sorry, we could not find any round data for this tournament 😔
            </div>
        );
    }

    const currentRoundData = rounds[currentRound] || {};

    // Memoize the cumulative scores calculation
    const cumulativeScores = useMemo(() => {
        const scores: number[] = [];;
        let totalScore = 0;

        // Calculate cumulative scores for each hole
        currentRoundData.Holes.forEach((hole) => {
            totalScore += hole.NetScore; 
            scores.push(totalScore);
        });

        return scores;
    }, [currentRound]);

    const handleRoundChange = (event: React.ChangeEvent<HTMLSelectElement>) => {
        const selectedRound = rounds.length - Number(event.target.value);
        console.log(selectedRound);
        setCurrentRound(selectedRound);
        setSelectCurrentRound(Number(event.target.value))
    };

    return (
        <div className="w-full p-4 border-y-2">
            {/* Summary Card */}
            <div className="w-full p-4 mb-4 bg-middle rounded-lg shadow-md flex flex-col items-center">
                <div className="grid grid-cols-3 gap-2 w-full mb-3">
                    <select
                        id="round-select"
                        className="p-2 rounded-lg w-1/3 text-center cursor-pointer bg-middle shadow border-dark-2 lg:text-md md:text-md sm:text-sm text-md"
                        onChange={handleRoundChange}
                        value={selectCurrentRound}
                        disabled={rounds.length === 0}
                    >
                        <option value="" disabled>
                            {rounds.length > 0 ? "Choose a Round" : "No rounds available"}
                        </option>
                        {rounds
                            .slice()
                            .map((_, index) => (
                                <option key={index} value={rounds.length - index}>
                                    Round {rounds.length - index}
                                </option>
                            ))}
                    </select>
                    <h2 className="text-xl font-bold mb-2 font-PTSans text-center hover:cursor">        
                        Round Summary 
                        
                        { showSummary ?
                            <span 
                            className="text-sm hover:cursor-pointer ml-1"
                            onClick={() => setShowSummary(!showSummary)}
                            >
                                ⬆
                            </span>
                            :
                            <span 
                            className="text-sm hover:cursor-pointer ml-1"
                            onClick={() => setShowSummary(!showSummary)}
                            >
                                ⬇
                            </span>
                        }
                        

                    </h2>
                </div>
                { showSummary ?
                    <>
                        <div className="flex flex-col items-center w-full">
                            <div className="grid grid-cols-7 gap-2 text-center text-sm">
                                <div>
                                    <span role="img" aria-label="albatross">🌟</span>
                                    <p>Albatross: {currentRoundData.Albatross}</p>
                                </div>
                                <div>
                                    <span role="img" aria-label="eagle">🦅</span>
                                    <p>Eagles: {currentRoundData.Eagles}</p>
                                </div>
                                <div>
                                    <span role="img" aria-label="birdie">🐥</span>
                                    <p>Birdies: {currentRoundData.Birdies}</p>
                                </div>
                                <div>
                                    <span role="img" aria-label="pars">⛳</span>
                                    <p>Pars: {currentRoundData.Pars}</p>
                                </div>
                                <div>
                                    <span role="img" aria-label="bogey">☠️</span>
                                    <p>Bogeys: {currentRoundData.Bogeys}</p>
                                </div>
                                <div>
                                    <span role="img" aria-label="double bogey">💀</span>
                                    <p>Double Bogeys: {currentRoundData.DoubleBogeys}</p>
                                </div>
                                <div>
                                    <span role="img" aria-label="worse than double bogeys">🪦</span>
                                    <p>Worse: {currentRoundData.WorseThanDoubleBogeys}</p>
                                </div>
                            </div>
                        </div>
                        <p className="mt-4 text-lg font-semibold">Score: {currentRoundData.Score}</p>
                    
                    </>                    
                    :
                    null
                }
            </div>

            {/* Holes Comparison Chart */}
            <div className="flex flex-row p-2">
                <THead datapoint="Holes" />
                {Array.from({ length: 18 }, (_, i) => (
                    <THead key={i} datapoint={i + 1} />
                ))}
            </div>
            <div className="flex flex-row p-2">
                <TData>Par</TData>
                {holes.map((hole) => (
                    <TData>{hole.Par}</TData>
                ))}
            </div>
            <div className="flex flex-row p-2">
                <TData>Strokes</TData>
                    {currentRoundData?.Holes.map((hole, idx) => {
                        
                        let strokes: number | string = hole.Strokes;
                        if (hole.Strokes === 0 || null) {
                            strokes = "--";
                        }
                        return ( 
                        <div key={idx} className="flex-grow flex items-center justify-center w-8">   
                            <ScoreWrapper score={hole.NetScore}>
                                <TData>{strokes}</TData>
                            </ScoreWrapper>
                        </div>
                        )
                    })}
                    {/* Fill missing holes with placeholders */}
                    {Array.from({ length: 18 - currentRoundData?.Holes.length }).map((_, idx) => (
                        <div key={`placeholder-${idx}`} className="flex-grow flex items-center justify-center w-8">
                            <TData>--</TData>
                        </div>
                    ))}
            </div>
            <div className="flex flex-row p-2">
                <TData>Ovr</TData>
                {cumulativeScores.map((score) => {
                    let cumulativeScore: number | string = score;
                    if (cumulativeScore === 0) {
                        cumulativeScore = "E";
                    }

                    return (
                        <div className="flex-grow flex items-center justify-center w-8"> 
                            <TData>{cumulativeScore}</TData>
                        </div>
                    )

                })}
            </div>
        </div>
    );
}
