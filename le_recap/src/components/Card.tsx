import React from 'react';

interface CardProps {
  // Optional prop in case you want to pass custom text lines dynamically
  lines?: string[];
}

const Card: React.FC<CardProps> = ({ 
  lines = [
    "wefwfe RECAP thing 001110110101",
    "next line",
    "woah",
    "ok fire",
    "this works??!?!?!!!",
    "aaaaaaaaaaa"
  ] 
}) => {
  
  // Type-safe styles using React.CSSProperties
  const styles: {
    container: React.CSSProperties;
    line: React.CSSProperties;
  } = {
    container: {
      width: '100%',
      maxWidth: '500px', 
      minHeight: '650px', 
      backgroundImage: "url('../assets/page.png')",
      backgroundSize: '100% 100%',
      backgroundRepeat: 'no-repeat',
      boxSizing: 'border-box',
      paddingTop: '60px',       // Spaces the text down from the top edge
      paddingLeft: '110px',     // Indents the text to sit to the right of the red line
      paddingRight: '40px',
      fontFamily: "'Jersey 10', sans-serif",
      fontSize: '24px',         
      color: '#000000',
      letterSpacing: '0.5px',
      textAlign: 'left',
    },
    line: {
      lineHeight: '34px',       // Adjust to match the visual spacing of your specific image
      margin: 0,
      minHeight: '34px',        // Prevents empty lines from collapsing
    }
  };

  return (
    <>
      {/* Injecting the Google Font directly */}
      <style>
        {`@import url('https://fonts.googleapis.com/css2?family=Jersey+10&display=swap');`}
      </style>

      <div style={styles.container}>
        {lines.map((line, index) => (
          <p key={index} style={styles.line}>
            {line}
          </p>
        ))}
      </div>
    </>
  );
};

export default Card;