// src/components/PaperDeck.tsx
import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence, type Variants } from 'framer-motion';
import pageImage from '../assets/page.png';

const JERSEY_FONT = "'Jersey 10', sans-serif";

interface CardData {
  id: string | number;
  content: string[];
}

interface PaperDeckProps {
  cards: CardData[];
}

export const PaperDeck: React.FC<PaperDeckProps> = ({ cards }) => {
  // Track the current active card index instead of a count
  const [currentIndex, setCurrentIndex] = useState<number>(0);

  const nextCard = () => {
    if (currentIndex < cards.length - 1) {
      setCurrentIndex((prev) => prev + 1);
    }
  };

  const prevCard = () => {
    if (currentIndex > 0) {
      setCurrentIndex((prev) => prev - 1);
    }
  };

  // Handle click zones based on screen position
  const handleScreenClick = (e: React.MouseEvent<HTMLDivElement>) => {
    const halfWidth = window.innerWidth / 2;
    if (e.clientX > halfWidth) {
      nextCard();
    } else {
      prevCard();
    }
  };

  // Handle Arrow key presses
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.key === 'ArrowRight') {
        nextCard();
      } else if (e.key === 'ArrowLeft') {
        prevCard();
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, [currentIndex, cards.length]); // Re-bind when index changes to keep current state fresh

  return (
    <div 
      onClick={handleScreenClick}
      style={{
        position: 'relative',
        width: '100vw',
        height: '100vh',
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        overflow: 'hidden',
        background: 'hsl(180, 14%, 31%)',
        cursor: 'pointer', // Indicates the screen is completely clickable
      }}
    >
      {/* Visual Navigation Hint Overlays (Invisible but functional guide) */}
      <div style={{ position: 'absolute', left: '20px', bottom: '20px', color: '#fff', opacity: 0.4, fontFamily: JERSEY_FONT, fontSize: '20px', pointerEvents: 'none' }}>
        {currentIndex > 0 ? '← Click Left / Arrow Left' : ''}
      </div>
      <div style={{ position: 'absolute', right: '20px', bottom: '20px', color: '#fff', opacity: 0.4, fontFamily: JERSEY_FONT, fontSize: '20px', pointerEvents: 'none' }}>
        {currentIndex < cards.length - 1 ? 'Click Right / Arrow Right →' : 'Done!'}
      </div>

      <div style={{ position: 'relative', width: '400px', height: '550px' }} onClick={(e) => e.stopPropagation()}>
        <AnimatePresence mode="popLayout">
          {/* 
            Only render cards up to the currentIndex. 
            When currentIndex decreases, the top card unmounts and plays its exit animation.
          */}
          {cards.slice(0, currentIndex + 1).map((card, index) => (
            <PaperSheet 
              key={card.id} 
              content={card.content} 
              index={index} 
            />
          ))}
        </AnimatePresence>
      </div>

      {currentIndex === cards.length - 1 && (
        <button
          onClick={(e) => {
            e.stopPropagation(); // Prevent triggering the page turn click
            alert("Share your Wrapped!");
          }}
          style={{
            position: 'absolute',
            right: '100px',
            fontFamily: JERSEY_FONT,
            fontSize: '24px',
            padding: '10px 24px',
            background: '#FFE066',
            border: '3px solid #000',
            cursor: 'pointer',
            boxShadow: '4px 4px 0px #000',
            zIndex: cards.length + 10, // Make sure it stays clickable on top of everything
          }}
        >
          SHARE RECAP
        </button>
      )}
    </div>
  );
};

// --- SUB-COMPONENT: Individual Stacking Paper Sheet ---

interface PaperSheetProps {
  content: string[];
  index: number;
}

const PaperSheet: React.FC<PaperSheetProps> = ({ content, index }) => {
  const randomRotation = React.useMemo(() => {
    const seed = index * 153.7;
    return Math.sin(seed) * 4;
  }, [index]);

  const dropVariants: Variants = {
    initial: {
      y: -800,
      opacity: 0,
      rotate: 0,
      scale: 1.05,
    },
    animate: {
      y: 0,
      opacity: 1,
      rotate: randomRotation,
      scale: 1,
      transition: {
        type: 'spring',
        stiffness: 65,
        damping: 15,
        mass: 1.1,
      },
    },
    exit: {
      y: -800, // Pulls the paper back up to the top when going backward
      opacity: 0,
      rotate: 0,
      scale: 1.05,
      transition: {
        type: 'spring',
        stiffness: 80,
        damping: 18,
      }
    }
  };

  return (
    <motion.div
      variants={dropVariants}
      initial="initial"
      animate="animate"
      exit="exit"
      style={{
        position: 'absolute',
        width: '100%',
        height: '100%',
        top: 0,
        left: 0,
        zIndex: index,
        backgroundImage: `url(${pageImage.src})`,
        backgroundSize: 'cover',
        backgroundPosition: 'center',
        boxShadow: '0px 10px 25px rgba(0,0,0,0.35), 0px 4px 10px rgba(0,0,0,0.2)',
        padding: '40px 30px 40px 65px',
        display: 'flex',
        flexDirection: 'column',
        boxSizing: 'border-box',
      }}
    >
      <div 
        style={{
          fontFamily: JERSEY_FONT,
          fontSize: '28px',
          color: '#1a1a1a',
          lineHeight: '1.45',
          letterSpacing: '0.5px',
          whiteSpace: 'pre-wrap',
          textAlign: 'left',
        }}
      >
        {content.map((line, i) => (
          <div key={i} style={{ minHeight: '32px' }}>
            {line}
          </div>
        ))}
      </div>
    </motion.div>
  );
};