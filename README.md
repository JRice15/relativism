# Relativism

Probabilistic music creation

## What is it?

Relativism is a project to edit, analyze,
and synthesize music. 


## How does it work?

Because the audio is typically stored at sample rates 44,000 samples per second, in stereo, 
editing of a full song requires millions of data points. To make this a usable program, nearly
all operations have been vectorized with NumPy.

## What can it do?
With easy commandline program interface, you can:
* read audio in many formats
* record audio live from any audio input
* write audio to .wav format
* edit audio, including:
    * slice, stretch, and slow
    * repeat and reverse
    * fade-in and out
    * save, demo, and undo changes
* apply common effects, such as:
    * bitcrushing
    * distortion
    * echo and reverb
* create and save projects
* use Samplers that generate output, with controlled randomness

## AutoDrummer

For the TensorFlow rhythm-matching system, see the AutoDrummer extension (another repo on my GitHub)
