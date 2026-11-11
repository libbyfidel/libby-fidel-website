"""Nav banner: a curved ribbon with folded tails and a horizontal label (inline SVG, coloured in assets/header.css).
Signature kept from the old sketch bow so tools/build-header.py is unchanged; mirror/extra/short are ignored."""
def sketch_bow(label,n,mirror=False,extra=0,short=0):
    tail=lambda f:f'<path class="paper tail" d="M{f(36)},38 L{f(2)},36 L{f(16)},60 L{f(2)},86 L{f(36)},86 Z"/><path class="paper fold" d="M{f(22)},74 L{f(36)},86 L{f(36)},66 Z"/>'
    return (f'<svg class="bow" viewBox="0 0 240 100" aria-hidden="true"><defs><path id="tp{n}" d="M22,60 Q120,40 218,60"/></defs>'
            f'{tail(lambda x:x)}{tail(lambda x:240-x)}<path class="paper" d="M22,26 Q120,6 218,26 L218,74 Q120,54 22,74 Z"/>'
            f'<text class="bt" text-anchor="middle"><textPath href="#tp{n}" startOffset="50%">{label}</textPath></text></svg>')
