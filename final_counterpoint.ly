\version "2.24.4"
\header {
  title = "First Species Counterpoint Example"
  subtitle = "Generated from MIDI Notes"
}

\score {
  <<
    \new Staff = "Counterpoint" <<
      \clef treble
      \key c \major
      \time 4/4
      \fixed c' { 
        c'1 | d'1 | e'1 | f'1 | g'1 | a'1 | b'1 | a'1 | g'1 | f'1 | e'1
      }
    >>
    \new Staff = "CantusFirmus" <<
      \clef treble
      \key c \major
      \time 4/4
      \fixed c' { 
        c1 | d1 | f1 | e1 | f1 | g1 | a1 | g1 | e1 | d1 | c1
      }
    >>
  >>
  \layout { }
  \midi { }
}
