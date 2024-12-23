import { useRef } from 'react';
import golfLinks from '../../../../assets/golf-links.png';
import GameCard from './GameCard';
import BackButton from '../../../Utils/components/BackButton';
import NextButton from '../../../Utils/components/NextButton';

export default function GamesCarousel() {

    // const games = [
    //     {
    //         gameName: "Stroke Play",
    //         desc: "In this game mode, golfers accumulate points as a team. Your objective to win is having the team with the score furthest below par combined.",
    //         minNumOfPlayers: 4,
    //         maxNumOfPlayers: 32,
    //         img: golfLinks
    //     },
    //     {
    //         gameName: "Best Ball",
    //         desc: "In this game mode, golfers accumulate points as a team. Your objective to win is having the team with the score furthest below par combined.",
    //         minNumOfPlayers: 4,
    //         maxNumOfPlayers: 32,
    //         img: golfLinks
    //     },
    //     {
    //         gameName: "Head to Head",
    //         desc: "In this game mode, golfers accumulate points as a team. Your objective to win is having the team with the score furthest below par combined.",
    //         minNumOfPlayers: 4,
    //         maxNumOfPlayers: 32,
    //         img: golfLinks
    //     },
    // ];

    const scrollContainer = useRef(null);

    const handleBackClick = () => {
        scrollContainer.current.style.scrollBehavior = 'smooth';
        scrollContainer.current.scrollLeft -= 400;
    };

    const handleNextClick = () => {
        scrollContainer.current.style.scrollBehavior = 'smooth';
        scrollContainer.current.scrollLeft += 400;
    };

    return (
        <div
        className='p-4 bg-dark'
        >
            <h1 className='p-3 text-4xl text-light font-PTSans'>Popular Games</h1>
            <div 
            className='flex justify-center items-center align-center'>
                <div className='justify-center w-8'>
                    <BackButton handleBackClick={handleBackClick} />
                </div>
                <div 
                className='flex justify-center items-center mt-3 w-full scrollbar-hide'
                >
                    <div 
                    className='flex overflow-x-auto items-center scrollbar-hide'
                    >
                        <div 
                        className='flex flex-nowrap overflow-x-auto overflow-scroll scrollbar-hide w-full align-baseline' 
                        ref={scrollContainer}
                        >
                            <div 
                            className='flex items-center justify-center m-auto scrollbar-hidden'
                            >
                                {games.map((game) => { 
                                    return <GameCard game={game} />
                                })}
                            </div>
                        </div>
                    </div>
                    {/* handle the click to the next flashcard */}
                    
                </div>
                <div className='justify-center w-8'>
                    <NextButton handleNextClick={handleNextClick} />
                </div>
            </div>
        </div>
    )
}