import React, { useState, useRef } from "react";
import {
  motion,
  useTransform,
  AnimatePresence,
  useMotionValue,
  useSpring,
} from "framer-motion";
import { useDispatch } from "react-redux";
import { AppDispatch } from "../../../store";
import { setSelectedGolfer } from "../state/golferSlice";
import { Golfer } from "../../../types/golfers";
import { Portal } from "react-portal";

interface AnimatedTooltipStartersProps {
  players: Golfer[] | undefined;
}


const AnimatedTooltipStarters: React.FC<AnimatedTooltipStartersProps> = ({ players }) => {
    const dispatch = useDispatch<AppDispatch>();
    const [hoveredIndex, setHoveredIndex] = useState<number | null>(null);
  
    const imageRefs = useRef<(HTMLDivElement | null)[]>([]); // Array to store references to each player's image
    const tooltipRefs = useRef<(HTMLDivElement | null)[]>([]); // Array to store references to each tooltip
  
    const springConfig = { stiffness: 100, damping: 5 };
    const x = useMotionValue(0);
    const rotate = useSpring(useTransform(x, [-100, 100], [-45, 45]), springConfig);
    const translateX = useSpring(useTransform(x, [-100, 100], [-50, 50]), springConfig);
  
    const handleMouseMove = (event: any) => {
        const halfWidth = event.target.offsetWidth / 2;
        x.set(event.nativeEvent.offsetX - halfWidth); // set the x value, which is then used in transform and rotate
    };
  
    const handleGolferClick = (golfer: Golfer) => {
      dispatch(setSelectedGolfer(golfer));
    };
  
    return (
      <div className="flex flex-row w-full font-PTSans">
        {players?.map((player, idx) => (
          <div
            key={player.id}
            className="-mr-4 relative group"
            onMouseEnter={() => setHoveredIndex(idx)}
            onMouseLeave={() => setHoveredIndex(null)}
          >
            <AnimatePresence mode="popLayout">
              {hoveredIndex === idx && (
                <Portal>
                  <motion.div
                    initial={{ opacity: 0, y: 20, scale: 0.4 }}
                    animate={{
                      opacity: 1,
                      y: 0,
                      scale: 1,
                      transition: {
                        type: "spring",
                        stiffness: 260,
                        damping: 10,
                      },
                    }}
                    exit={{ opacity: 0, y: 20, scale: 0.4 }}
                    style={{
                      position: "absolute",
                      rotate: rotate,
                      translateX: translateX,
                      // Calculate tooltip's top and left positions dynamically
                      top: imageRefs.current[idx]
                        ? `${imageRefs.current[idx].getBoundingClientRect().top - 60}px`
                        : "0px", // Adjust vertical offset as needed
                      left: imageRefs.current[idx]
                        ? (() => {
                            const imageRect = imageRefs.current[idx]!.getBoundingClientRect();
                            const tooltipLeft = imageRect.left + ((imageRect.width / 2) - 70);
  
                            return `${tooltipLeft}px`;
                          })()
                        : "0px", // Adjust horizontal positioning based on image
                      zIndex: 1000, // Ensure the tooltip is above other elements
                    }}
                    ref={(el) => (tooltipRefs.current[idx] = el)} // Attach ref to each tooltip dynamically
                    className="absolute flex text-xs flex-col items-center justify-center rounded-md bg-dark z-50 shadow-xl px-4 py-2"
                  >
                    <div className="absolute inset-x-10 z-30 w-[20%] -bottom-px bg-gradient-to-r from-transparent via-middle to-transparent h-px" />
                    <div className="absolute left-10 w-[40%] z-30 -bottom-px bg-gradient-to-r from-transparent via-highlightBlue to-transparent h-px" />
                    <div className="font-bold text-light relative z-30 text-base">
                      {`${player.FirstName} ${player.LastName}`}
                    </div>
                    <div className="text-light text-xs">Rank: {player.Rank}</div>
                  </motion.div>
                </Portal>
              )}
            </AnimatePresence>
            <div
              onMouseMove={(event) => handleMouseMove(event)}
              onClick={() => handleGolferClick(player)}
              className="flex items-center justify-center w-12 h-12 rounded-full border-2 border-dark bg-light group-hover:scale-105 transition-transform cursor-pointer relative overflow-hidden"
              ref={(el) => (imageRefs.current[idx] = el)} // Attach ref to each image dynamically
            >
              <img
                src={"/default-avatar.png"}
                alt={`${player.FirstName} ${player.LastName}`}
                className="object-cover !m-0 !p-0 object-top rounded-full h-14 w-14 border-2 group-hover:scale-105 group-hover:z-30 border-dark relative transition duration-500"
              />
            </div>
          </div>
        ))}
      </div>
    );
  };
  
  export default AnimatedTooltipStarters;