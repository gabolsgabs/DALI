import copy
import numpy as np


def get_delay(cross_corr, auto_corr):
    cross_p = np.argmax(cross_corr)
    auto_p = np.argmax(auto_corr)
    return auto_p - cross_p


def crosscorrelation(base, query):
    npmax = np.max
    npcorrelate = np.correlate
    cross = npcorrelate(query, base, mode='same')
    cross_max = npmax(cross)
    auto_base = npcorrelate(base, base, mode='same')
    base_max = npmax(auto_base)
    auto_query = npcorrelate(query, query, mode='same')
    query_max = npmax(auto_query)
    dist = cross_max / np.sqrt(base_max * query_max)
    """
    dist_base = cross_max / base_max
    dist_query = cross_max / query_max
    balance = get_balance(base, query)
    """
    confi = np.power(cross_max, 2) / (base_max * query_max)
    delay = get_delay(cross, auto_base)
    """
    delay > 0 add silence at the begining -> move to right
    delay < 0 add silence at the end -> move to left
    """
    images = cross, auto_base, auto_query
    return dist, confi, delay, images


def align_brute_force(entry, pred, g, r=(1./100), s=.2):
    ref_fr = entry.annotations['annot_param']['fr']
    ref_offset = entry.annotations['annot_param']['offset']
    rng = ref_fr*r
    step = rng*s
    time_r = 0.014
    best = [0., 0., 0.]
    print("Aligning " + entry.info['artist'] + ' ' + entry.info['title'])
    for fr in np.arange(ref_fr-rng-step, ref_fr+rng+step, step):
        tmp = copy.deepcopy(entry)
        tmp.change_time(new_fr=fr)
        annot = tmp.get_annot_as_vector_chopping()
        dist, _, delay, _ = crosscorrelation(pred, annot)
        if dist > best[0]:
            best[0] = dist
            best[1] = fr
            best[2] = ref_offset + delay*time_r
    return best


def align_offset(entry, pred, g):
    print("Aligning " + entry.info['artist'] + ' ' + entry.info['title'])
    time_r = 0.014
    annot = entry.get_annot_as_vector_chopping()
    dist, _, delay, _ = crosscorrelation(pred, annot)
    ref_offset = entry.annotations['annot_param']['offset']
    return dist, ref_offset + delay*time_r
