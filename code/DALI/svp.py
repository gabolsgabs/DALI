import math
import numpy as np
from .utilities_audio import read_MP3
from numpy.fft import irfft


def mel2hz(mel):
    # Converting mel to hz
    return 700*(math.exp(mel/1125) - 1)


def hz2bin(Nfft, Fe, m):
    # Converting a mel-frequency to bin
    return math.floor((Nfft+1)*mel2hz(m)/Fe)


def hz2mel(hz):
    # Converting hz to mel
    return 1125*math.log(1+hz/700.0)


def F_compute_mel(startBin, endBin, centerBin):
    """
    Compute a triangular filter
       startBin : start bin of the filter
       centerBin : center bin of the filter
       Bin :  bin of the filter
    """

    melFilter_v = np.zeros((endBin-startBin+1, 1))
    if endBin-startBin < 3:
        melFilter_v = np.ones((endBin-startBin+1, 1))
    else:
        i = 1
        for k in range(startBin, endBin):
            if k >= startBin and k <= centerBin:
                melFilter_v[i] = ((k)-startBin)/(centerBin-startBin)
            if k >= centerBin and k <= endBin:
                melFilter_v[i] = ((endBin)-k)/(endBin-centerBin)
            i = i+1
    return melFilter_v


def ms(x):
    """Mean value of signal `x` squared.
    :param x: Dynamic quantity.
    :returns: Mean squared of `x`.
    """
    return (np.abs(x)**2.0).mean()


def normalize(y, x=None):
    """normalize power in y to a (standard normal) white noise signal.
    Optionally normalize to power in signal `x`.
    #The mean power of a Gaussian with :math:`\\mu=0` and :math:`\\sigma=1` is 1.
    """
    if x is not None:
        x = ms(x)
    else:
        x = 1.0
    return y * np.sqrt(1 / ms(y))


def pink(N, state=None):
    """
    Pink noise.

    :param N: Amount of samples.
    :param state: State of PRNG.
    :type state: :class:`np.random.RandomState`

    Pink noise has equal power in bands that are proportionally wide.
    Power density decreases with 3 dB per octave.

    """
    state = np.random.RandomState() if state is None else state
    uneven = N % 2
    X = state.randn(N//2+1+uneven) + 1j * state.randn(N//2+1+uneven)
    S = np.sqrt(np.arange(len(X))+1.)  # +1 to avoid divide by zero
    y = (irfft(X/S)).real
    if uneven:
        y = y[:-1]
    return normalize(y)


def stft(signal_v, overlapFac, frame_size, window=np.hanning):

    win = np.hanning(frame_size)
    aa = overlapFac*np.arange(int((len(signal_v)-frame_size)/overlapFac+1))
    S = np.array([np.fft.rfft(win[::-1]*signal_v[b:b+frame_size], n=1024)
                  for b in aa]).T
    return (np.abs((S**2)))


def get_mls(x, sr, overlap, frame_size):
    spec = stft(x, overlap, frame_size)
    context = 0.84
    nbFft = spec[1]
    nbBinPink = context * sr
    pinkNoise = pink(int(nbBinPink))
    # overlapFac = overlap/frameSize
    pinkNoiseSpec = stft(pinkNoise, overlap, frame_size)
    ref = np.max(spec)
    magnitude = 10**((10*math.log(ref)-70)/10)
    pinkNoiseSpec = np.abs(pinkNoiseSpec)*magnitude
    nvSpec = np.concatenate((pinkNoiseSpec, spec, pinkNoiseSpec), axis=1)
    nbFft, nbTrame = nvSpec.shape
    lowFreq = 27.5
    highFreq = 8000
    nFilter = 80
    eps = 10e-8
    melFilterBank_m = F_computeMelBank(nbFft, lowFreq, highFreq, nFilter, sr)
    output = np.dot(melFilterBank_m, nvSpec)
    clip_m = np.clip(output, eps, np.max(output))
    return np.log(clip_m)



def F_computeMelBank(nbBin, lowFreq, highFreq, nFilter, sampleRate,
                     affich=False):
    """
    Compute a Mel filters bank

       nbBin : number of bins in a filter
       lowFreq : lowest frenquency in the bank
      highFreq : highest frenquency in the bank
       nFilter : number of filters
       sampleRate : sample rate
       affich : to visualize the bank, set this value to true

       Filters is a nFilter by nbBin matrix, with nFilter triangular filters.
    """

    # Converting low_f and high_f in mel-scale
    low_mel = hz2mel(lowFreq)
    high_mel = hz2mel(highFreq)
    # m is a linspace with N+2 mel-frequency, lineary spaced
    melFreq = np.linspace(low_mel, high_mel, nFilter+2)

    # Converting m in Hz and then in bins in the fft
    try:
        binFreq = np.array(
            map(lambda x: int(hz2bin(nbBin, sampleRate, x)), melFreq))+1
    except Exception as e:
        binFreq = np.array(
            list(map(lambda x: int(hz2bin(nbBin, sampleRate, x)), melFreq)))+1

    # Initializing Filters
    filterBank_m = np.zeros((nFilter, nbBin))
    # Creating N triangular filters
    for i in range(0, nFilter):
        start = binFreq[i]         # start bin of the i-th filter
        center = binFreq[i+1]      # center bin of the i-th filter
        F = binFreq[i+2]           # bin of the i-th filter
        # Compute the actual triangular filter>
        filterBank_m[i, start:F+1] = np.transpose(
            F_compute_mel(start, F, center))
    return filterBank_m


def get_svp(audio_file, model):
    """
     For an audio file audioFile and a model (which path is modelPath)
     Compute the result of voice detection for the audio with the model.
       audio -> spec -> mell filtering -> logarithm scale -> excerpt passed
       througth the network -> value between 0 and 1 corresponding at the
       probability of the frame
    """
    print('Computing the SVP for ' + audio_file)
    signal_v, fe = read_MP3(audio_file, stereo2mono=True)
    output = []
    if np.max(signal_v) > 0.0:
        winLength_s = 0.046
        overlap_s = 0.014
        winLength_bin = int(winLength_s * fe)
        N = 115
        overlap_bin = int(overlap_s*fe)
        spect_m = get_mls(signal_v, fe, overlap_bin, winLength_bin)
        spect_m = np.transpose(spect_m)
        try:
            config = model.get_config()[0]['config']['data_format']
        except Exception as e:
            config = model.get_config()['layers'][0]['config']['data_format']

        nb_exemple = spect_m.shape[0]-115+1
        predict_v = []
        size_batch = 16
        nb_batch = nb_exemple // size_batch
        remain_examples = nb_exemple - nb_batch * size_batch
        cpt = 0
        for numExcerptBatch in range(nb_batch):
            start = cpt
            if config == 'channels_first':
                imBatch = np.zeros((size_batch, 1, N, 80))
            if config == 'channels_last':
                imBatch = np.zeros((size_batch, N, 80, 1))
            for j in range(size_batch):
                if config == 'channels_first':
                    imBatch[j, 0, :, :] = spect_m[start:start+N, :]
                if config == 'channels_last':
                    imBatch[j, :, :, 0] = spect_m[start:start+N, :]
                start += 1
            cpt += size_batch
            res = model.predict_on_batch(imBatch)
            predict_v.append(res)

        for num in range(remain_examples):
            start = num + cpt
            end = start + N
            if config == 'channels_first':
                im = np.zeros((1, 1, N, 80))
                im[0, 0, :, :] = spect_m[start:end, :]
            if config == 'channels_last':
                im = np.zeros((1, N, 80, 1))
                im[0, :, :, 0] = spect_m[start:end, :]
            res = model.predict_on_batch(im)  # what the CNN predict
            predict_v.append(res[0])
        output = np.array([np.float(i) for j in predict_v for i in j])
    return output
