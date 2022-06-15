# system imports
import argparse
from re import S

# additional imports
import torch
import note_seq
from music21 import *

# internal imports
import improv_rnn



def main(args):    
    # Load model from checkpoint
    loaded_checkpoint = torch.load(args.model, map_location=torch.device('cpu'))
    encoder = loaded_checkpoint['encoder']

    model = improv_rnn.ImprovRNN(encoder, 1)
    model.load_state_dict(loaded_checkpoint['model_state'])
    model.eval()
   
    generated_sequence, _, _, melody_events, chords = improv_rnn.generate_sequnce(encoder, model, backing_chords=args.backing_chords, steps_per_chord=args.steps_per_chord)
    create_score(melody_events, chords)
    note_seq.note_sequence_to_pretty_midi(generated_sequence).write(args.output)



def create_score(melody_events, chords):
    #do stuff

    print(melody_events)

    #melody_events = [60, -1, -2, -2, 65, -2, 62, -2, 62, -2, -1, -2, 62, -2, 62, -2, 62, -2, -1, -2, 62, -2, -1, -2,63, -2, 62, -2, 62, -2, 62, -2, -1, -2, 64, -2, 62, -2, -2, -2, -2, -2, 60, -2, -2, -2, 55, -2, 60, -2, -1, -2, 64, -2, 60, -2, 64, -2, 60, -2, 60, -2, -1, -2, 65, -2, 62, -2, -2, -2, -2, -2,62, -2, -2, -2, 60, -2, 65, -2, -1, -2, 67, -2, 64, -2, 64, -2, 64, -2, 60, -2, -2, -2, 64, -2,65, -2, -2, -2, -1, -2, 65, -2, -2, -2, 65, -2, 65, -2, -2, -2]
    #print(melody_events)

    s = stream.Score(id='Improv RNN')
    p0 = stream.Part(id='Base') #todo
    p1 = stream.Part(id='Melody')

    # Abtastrate: taste jedes achtel/viertel etc ab, spiele neue Note oder verlängere die vorhandene Note

    step = 1
    smallest = 0.25

    for i in range(int(len(melody_events) / step)):
        dur = smallest
        i = i * step
        if(melody_events[i] > 0):
            for j in range(i + 1, int(len(melody_events) - step + 1), step):
                if(melody_events[j + step - 1] < 0):
                    dur = dur + smallest
                else:
                    break
            p1.append(note.Note(melody_events[i], duration=duration.Duration(dur)))
    
    for chord in chords:
        h = harmony.ChordSymbol(chord)
        h.duration = duration.Duration(4)
        h.writeAsChord = True
        p0.append(h)
    
    s.append(meter.TimeSignature('4/4'))
    s.append(p1)
    s.append(p0)
    #s.show()
    s.write("musicxml", "melody_rnn_test")



if __name__ == "__main__":
    # parse command line options
    parser = argparse.ArgumentParser(description='Generate melody given a chord sequence.')
    parser.add_argument("--backing_chords", default="C G Am F C G F C", type=str, help="Chord sequence.")
    parser.add_argument("--steps_per_chord", default=16, type=int, help="Number of steps per chord, 4 steps = 1 quarter note duration.")
    parser.add_argument("--model", default="checkpoints/checkpoint_950_triplets.pth", type=str, help="Path to model checkpoint.")
    parser.add_argument("--output", default="out.mid", type=str, help="Filename of output midi file.")
    args = parser.parse_args()

    main(args)