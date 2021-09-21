
def clapper(trope, repeat, reverse=False, wraparound=False):
    index = 0
    offset = 0
    wraps = len(trope)

    if wraparound:
        wraps += 1
    for j in range(wraps):
        for k in range(len(trope)):
            for i in range(repeat):
                layer = []
                layer.append(trope[(index % len(trope))])
                layer.append(trope[(index + offset) % len(trope)])

                yield layer
                index += 1
        if reverse:
            offset -= 1
        else:
            offset += 1

if __name__ == '__main__':

    print([x for x in clapper([1,2,3], 1, True, True)])

    print([x for x in clapper("ABCD", 2, True)])

