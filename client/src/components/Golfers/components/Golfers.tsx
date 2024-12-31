import PlayerData from "./PlayerData";
import TableHeaders from "../../Utils/components/TableHeaders"
import React, { useEffect } from "react";
import { useInView } from "react-intersection-observer";
import SkeletonTable from "../../Utils/components/SkeletonTable";
import LoadingWidget from "../../Utils/components/LoadingWidget";
import { Golfer } from "../../../types/golfers";

interface Page {
    golfers: Golfer[];
    nextPage: number | null | undefined;
}

interface GolfersProps {
    headers: string[];
    data: Page[] | null;
    isFetching: boolean;
    hasNextPage: boolean;
    isFetchingNextPage: boolean;
    fetchNextPage: () => void;
    onGolferClick: (golfer: object) => void;
    onAddClick: (golferId: string) => void;
  }
  
const Golfers = ({ headers, data, isFetching, hasNextPage, fetchNextPage, isFetchingNextPage, onGolferClick, onAddClick }: GolfersProps) => {
    const { ref, inView } = useInView();

    useEffect(() => {
        if (inView && hasNextPage) {
            fetchNextPage();
        };
    }, [inView, fetchNextPage]);

    return (
        <div className="w-full h-full overflow-auto text-light font-PTSans break-all bg-middle p-2">
            <div>
                <TableHeaders headers={headers} />
            </div>
            {data?.map((page, pageIndex) => (
                <div 
                key={pageIndex + (page.nextPage || 0)}
                >
                    {page.golfers.map((golfer, idx) => (
                        <div className="flex gap-2">
                        <PlayerData
                            key={golfer.id}
                            even={idx % 2 == 0}
                            player={golfer}
                            onClick={() => onGolferClick(golfer)}
                        />
                        <button 
                        className="bg-transparent text-dark p-2 rounded-full border-2 border-dark text-center hover:bg-light" 
                        onClick={(e) => {
                            e.stopPropagation(); // Prevent triggering the parent row's onClick
                            onAddClick(golfer.id);
                        }}
                        >
                            +
                        </button>
                        </div>
                    ))}
                </div>
            ))}
            <div className="flex justify-center p-4">
                <div ref={ref}></div>
                {isFetching && <SkeletonTable />}
                {isFetchingNextPage && <LoadingWidget />}
            </div>
        </div>
    );
}


export default Golfers;