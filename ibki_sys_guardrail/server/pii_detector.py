import re
from typing import Dict, List, Literal, Optional, Pattern, Tuple, TypedDict


PiiType = Literal[
    "rrn",          # 주민등록번호
    "name",         # 성명 (간단 휴리스틱)
    "account",      # 계좌번호 (일반적 패턴)
    "phone",        # 전화번호 (국내)
    "email",        # 이메일
    "address",      # 주소 (간단 휴리스틱)
]


class PiiMatch(TypedDict):
    type: PiiType
    value: str
    span: Tuple[int, int]


class PiiPattern(TypedDict):
    type: PiiType
    regex: Pattern[str]
    group: int


def _compile_patterns(include_foreigner_rrn: bool = True) -> List[PiiPattern]:
    flags = re.VERBOSE | re.UNICODE

    # 1) 주민등록번호: YYMMDD-[1-4]######  (선택: [5-8] 외국인등록번호)
    #   - 월/일 유효성 분기 강화
    #   - 숫자 경계 보장
    #   - 외국인 허용 여부 로직 수정 (기존 코드의 조합 버그 보완)
    rrn_gender = r"(?:[1-4]" + (r"|[5-8]" if include_foreigner_rrn else r"") + r")"
    rrn = re.compile(
        rf"""
        (?<!\d)
        (?:                                   # 생년월일(YYMMDD)
            \d{{2}}
            (?:
                (?:0[13578]|1[02])            # 01,03,05,07,08,10,12
                (?:0[1-9]|[12]\d|3[01])       # 01-31
              |
                (?:0[469]|11)                 # 04,06,09,11
                (?:0[1-9]|[12]\d|30)          # 01-30
              |
                02
                (?:0[1-9]|1\d|2[0-9])         # 01-29 (윤년은 사후체크 권장)
            )
        )
        [\s-]?                                # 구분자 선택
        {rrn_gender}\d{{6}}                   # 성별/세대 코드 + 6자리
        (?!\d)
        """,
        flags
    )

    # 2) 전화번호 (대한민국)
    #   - 대표번호(15/16/18xx) 포함
    #   - 국번/자리수 범위 엄격화
    #   - 확장(ext) 등 뒤따르는 숫자 꼬리 방지
    phone = re.compile(
        r"""
        (?<!\d)
        (?:                                  # 일반/이동/지역
            (?:\+82[\s-]?)?0?
            (?:
                10|11|16|17|18|19            # 이동통신 (010, 011 등)
              | 2                            # 02
              | [3-6][1-5]                   # 031-065 대역 (보수적으로 설정)
            )
            (?:[\s-]?\d{3,4}){2}
          |
            (?:\+82[\s-]?)?0?(?:15|16|18)\d{2}[\s-]?\d{4}   # 대표번호 15xx/16xx/18xx-xxxx
        )
        (?!\d)
        """,
        flags
    )

    # 3) 이메일 (ASCII 로컬 + 다중 서브도메인)
    #   - 주변 문자가 이메일 구성문자일 경우 제외
    email = re.compile(
        r"""
        (?<![A-Za-z0-9._%+\-])
        [A-Za-z0-9._%+\-]+
        @
        (?:[A-Za-z0-9\-]+\.)+[A-Za-z]{2,63}
        (?![A-Za-z0-9._%+\-])
        """,
        flags
    )

    # 4) 카드번호(16자리) - 오탐 방지를 위해 정규식은 조금 보수적으로,
    #   - BIN(첫자리 2~6) 범위로 시작 (현대 카드 스킴 일반)
    #   - 매치 후 Luhn 필수 권장 (POST_VALIDATORS 사용)
    card16 = re.compile(
        r"""
        (?<!\d)
        (?:[2-6]\d{3}[\s-]?){3}\d{4}
        (?!\d)
        """,
        flags
    )

    # 5) 계좌번호(국내 일반형) 오탐 최소화
    #   - **하이픈/공백 최소 1개** 강제 → 연속 숫자열 오탐 억제
    #   - 총 자릿수 9~14 (사후검증) + 주민/전화/카드 패턴과 상호배제
    #   - 그룹당 2~6자리, 그룹 수 2~5
    account = re.compile(
        r"""
        (?<!\d)
        (?!                                   # 주민번호 제외
           (?:\d{2}(?:0[1-9]|1[0-2])(?:0[1-9]|[12]\d|3[01]))[\s-]?(?:[1-8]\d{6})
        )
        (?!                                   # 전화번호 제외 (대표번호 포함)
           (?:
             (?:\+82[\s-]?)?0?(?:(?:10|11|16|17|18|19)|2|[3-6][1-5])(?:[\s-]?\d{3,4}){2}
            |(?:\+82[\s-]?)?0?(?:15|16|18)\d{2}[\s-]?\d{4}
           )
        )
        (?!                                   # 카드번호(16) 제외
            (?:[2-6]\d{3}[\s-]?){3}\d{4}
        )
        (?:\d{2,6}[\s-]+\d{2,6}(?:[\s-]+\d{2,6}){0,3})   # 하이픈/공백이 최소 1회 이상
        (?!\d)
        """,
        flags
    )
    # -> 매치 후: 하이픈/공백 제거 숫자길이 9~14 확인 (사후검증 훅)

    # 6) 성명(한글 2~4자, 흔한 성 + 1~3자) 오탐 억제
    #   - 성 뒤에 '길/로/구/군/시/면/동/리' 등 행정어미 바로 등장 금지
    #   - 앞/뒤에 한글/영문/숫자 붙는 케이스 금지
    #   - (선택) 호칭(님/씨/군/양/과장/대리 등) 붙은 경우 가중치 ↑ → 정규식에선 옵션으로 허용
    common_surnames = "김|이|박|최|정|강|조|윤|장|임|오|한|신|서|권|황|안|송|류|전|홍|고|문|손|배|백|허|유|남|노|양|심|변|주|우|민|진|탁|하|설|제|길"
    honorifics = "님|씨|군|양|과장|대리|팀장|차장|부장|박사|교수"
    name = re.compile(
        rf"""
        (?<![가-힣A-Za-z0-9])
        (?:{common_surnames})
        (?!길|로|구|군|시|면|동|리)         # 성 바로 뒤에 행정 어미 금지
        [가-힣]{{1,3}}
        (?:\s?(?:{honorifics}))?            # 선택적 호칭
        (?![가-힣A-Za-z0-9])
        """,
        flags
    )

    # 7) 주소(휴리스틱) 오탐 억제
    #   - 도/시/군/구 레이어 또는 도로명/지번 + 숫자 필수
    #   - 너무 짧은 로/길/번길 토큰 단독 매치 억제(앞뒤 경계, 최소 글자수)
    #   - 호/동/리/번지 패턴 숫자 요구
    address = re.compile(
        r"""
        (?<![가-힣0-9])
        (?:
            (?:[가-힣]{2,}(?:특별시|광역시|특별자치시|도)\s+[가-힣]{1,}(?:시|군|구)\s+(?:[가-힣]{1,}(?:읍|면)\s+)?)
            (?:
                [가-힣0-9]{2,}(?:로|길|번길)\s*\d{1,4}(?:-\d{1,4})?(?:\s*\d{1,4}호)?
              |
                [가-힣0-9]{2,}(?:동|리)\s*\d{1,4}(?:-\d{1,4})?(?:\s*\d{1,4}호)?
            )
          |
            [가-힣0-9]{2,}(?:로|길|번길)\s*\d{1,4}(?:-\d{1,4})?(?:\s*\d{1,4}호)?
          |
            [가-힣0-9]{2,}(?:동|리)\s*\d{1,4}(?:-\d{1,4})?(?:\s*\d{1,4}호)?
        )
        (?![가-힣0-9])
        """,
        flags
    )

    patterns: List[PiiPattern] = [
        {"type": "rrn",     "regex": rrn,     "group": 0},
        {"type": "phone",   "regex": phone,   "group": 0},
        {"type": "email",   "regex": email,   "group": 0},
        {"type": "card16",  "regex": card16,  "group": 0},
        {"type": "account", "regex": account, "group": 0},
        #{"type": "name",    "regex": name,    "group": 0},
        {"type": "address", "regex": address, "group": 0},
    ]
    return patterns

def __dummy_compile_patterns(include_foreigner_rrn: bool = True) -> List[PiiPattern]:
    flags = re.VERBOSE | re.UNICODE

    # 1) 주민등록번호: YYMMDD-[1-4]######  (선택: [5-8] 외국인등록번호)
    #   - 월/일 유효성: 31일/30일/2월(1-29일) 분기
    #   - 하이픈/공백 선택, 숫자 경계 보장
    rrn_gender = r"[1-4]" + (r"[5-8]?" if not include_foreigner_rrn else r"|[5-8]")
    rrn = re.compile(
        rf"""
        (?<!\d)
        (?:                                   # 생년월일(YYMMDD)
            \d{{2}}
            (?:
                (?:0[13578]|1[02])            # 01,03,05,07,08,10,12
                (?:0[1-9]|[12]\d|3[01])       # 01-31
              |
                (?:0[469]|11)                 # 04,06,09,11
                (?:0[1-9]|[12]\d|30)          # 01-30
              |
                02                             # 02월
                (?:0[1-9]|1\d|2[0-9])         # 01-29 (윤년 29일은 정규식에서 허용, 필요시 사후체크)
            )
        )
        [\s-]?                                # 구분자 선택
        (?:{rrn_gender})\d{{6}}               # 성별/세대 코드 + 6자리
        (?!\d)
        """,
        flags
    )

    # 2) 전화번호
    #    - +82 선택
    #    - 02-XXXX-XXXX (서울), 0xx-xxx(x)-xxxx (지역/이동통신)
    #    - 010 / 011/016/017/018/019 (레거시 포함)
    #    - 대표번호 15xx/16xx/18xx-xxxx
    phone = re.compile(
        r"""
        (?<!\d)
        (?:
            (?:\+82[\s-]?)?(?:0)?                  # 국가코드 + 0 선택
            (?:
                10|11|16|17|18|19|                # 이동통신 국번 (010 등; 011,016.. 포함)
                2|[3-6][1-5]                      # 지역번호 02 / 031-065 대역
            )
            [\s-]?\d{3,4}[\s-]?\d{4}
          |
            (?:\+82[\s-]?)?(?:0)?                 # 대표번호 (15xx/16xx/18xx)
            (?:15|16|18)\d{2}[\s-]?\d{4}
        )
        (?!\d)
        """,
        flags
    )

    # 3) 이메일 (일반적 ASCII 로컬파트 + 다중 서브도메인)
    email = re.compile(
        r"""
        (?<![A-Za-z0-9._%+\-])
        [A-Za-z0-9._%+\-]+
        @
        (?:[A-Za-z0-9\-]+\.)+[A-Za-z]{2,63}
        (?![A-Za-z0-9._%+\-])
        """,
        flags
    )

    # 4) 카드번호(16자리) - 계좌 오탐 방지를 위한 보조(탐지하거나, 최소한 제외용)
    card16 = re.compile(
        r"""
        (?<!\d)
        (?:\d{4}[\s-]?){3}\d{4}
        (?!\d)
        """,
        flags
    )

    # 5) 계좌번호(국내 일반형): 숫자/하이픈 조합, 총 자릿수 9~14 권장
    #    - 주민번호/전화번호/카드 패턴을 음수전방으로 배제
    #    - 하이픈 그룹 2~6자리 단위로 2~5그룹까지 허용
    account = re.compile(
        r"""
        (?<!\d)
        (?!                                     # 주민번호 제외
           (?:\d{2}(?:0[1-9]|1[0-2])(?:0[1-9]|[12]\d|3[01]))[\s-]?(?:[1-8]\d{6})
        )
        (?!                                     # 전화번호 제외 (대표번호 포함)
           (?:
             (?:\+82[\s-]?)?(?:0)?(?:(?:10|11|16|17|18|19)|2|[3-6][1-5])[\s-]?\d{3,4}[\s-]?\d{4}
            |(?:\+82[\s-]?)?(?:0)?(?:15|16|18)\d{2}[\s-]?\d{4}
           )
        )
        (?!                                     # 카드번호(16) 제외
            (?:\d{4}[\s-]?){3}\d{4}
        )
        (?:\d{2,6}(?:[\s-]?\d{2,6}){1,4})
        (?!\d)
        """,
        flags
    )
    #  -> 실운영에서는 위 정규식 매치 후, 하이픈/공백 제거한 숫자 길이가 9~14인지 **사후검증** 권장 (ChatGPT의 의견)

    # 6) 성명(한글 2~4자) : 상위 성씨 + 1~3 글자, 단어 경계 보장
    #    - 오탐 빈번한 행정/지명 어미(길/로/구/군/시/면/동/리 등) 회피
    common_surnames = "김|이|박|최|정|강|조|윤|장|임|오|한|신|서|권|황|안|송|류|전|홍|고|문|손"
    name = re.compile(
        rf"""
        (?<![가-힣A-Za-z0-9])
        (?:{common_surnames})
        (?!길|로|구|군|시|면|동|리)         # 성 바로 뒤에 행정 어미 금지
        [가-힣]{{1,3}}
        (?![가-힣A-Za-z0-9])
        """,
        flags
    )

    # 7) 주소(휴리스틱): [광역]시/도 + 시/군/구 + (읍/면)? + 동/리/로/길 + 번지/호
    #    - 도로명: '로|길|번길' + 번지(숫자[-숫자]?) + (호) 선택
    #    - 지번: 동/리 + (숫자[-숫자]? 번지) + (호)
    address = re.compile(
        r"""
        (?:
            [가-힣]{2,}(?:특별시|광역시|특별자치시|도)\s*
            [가-힣]{1,}(?:시|군|구)\s*
            (?:[가-힣]{1,}(?:읍|면)\s*)?
            (?:
                [가-힣0-9]{1,}(?:로|길|번길)\s*\d{1,4}(?:-\d{1,4})?(?:\s*\d{1,4}호)?
              |
                [가-힣0-9]{1,}(?:동|리)\s*\d{1,4}(?:-\d{1,4})?(?:\s*\d{1,4}호)?
            )
          |
            # 간단 도로명/지번 단독 탐지 (도/시 생략 케이스)
            [가-힣0-9]{1,}(?:로|길|번길)\s*\d{1,4}(?:-\d{1,4})?(?:\s*\d{1,4}호)?
          |
            [가-힣0-9]{1,}(?:동|리)\s*\d{1,4}(?:-\d{1,4})?(?:\s*\d{1,4}호)?
        )
        """,
        flags
    )

    patterns: List[PiiPattern] = [
        {"type": "rrn",     "regex": rrn,     "group": 0},
        {"type": "phone",   "regex": phone,   "group": 0},
        {"type": "email",   "regex": email,   "group": 0},
        {"type": "card16",  "regex": card16,  "group": 0},   # 필요시 탐지/제외용
        {"type": "account", "regex": account, "group": 0},
        {"type": "name",    "regex": name,    "group": 0},
        {"type": "address", "regex": address, "group": 0},
    ]
    return patterns
    

def _no_compile_patterns() -> List[PiiPattern]:
    # 주민등록번호: YYMMDD-ABCDEFG (하이픈 선택), 7번째 성별 코드 1-4
    rrn = re.compile(r"\b(\d{2}(?:0[1-9]|1[0-2])(?:0[1-9]|[12]\d|3[01]))-?(?:[1-4]\d{6})\b")

    # 한국 전화번호: 휴대폰, 지역번호 포함. 하이픈 선택
    phone = re.compile(
        r"\b(?:\+82[- ]?)?(?:0)?(?:(?:10|11|16|17|18|19)|2|[3-6][1-5])[- ]?\d{3,4}[- ]?\d{4}\b"
    )

    # 이메일: 일반적인 로컬@도메인 패턴
    email = re.compile(r"\b[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[A-Za-z]{2,}\b")

    # 계좌번호: 9~14자리 숫자, 선택적 하이픈 구분 (카드번호(16)와 전화번호 제외되도록 길이 제한)
    account = re.compile(r"\b(?:\d{2,4}-){1,3}\d{2,6}\b|\b\d{9,14}\b")

    # 성명: 한글 성명 2~4자. 너무 광범위하므로 단어 경계 고려
    name = re.compile(r"(?<![\w가-힣])(?!길|동|구|군|시)[가-힣]{2,4}(?![\w가-힣])")

    # 주소: 시/군/구 포함 간단 휴리스틱 (도로명/지번을 모두 완벽히 처리하진 않음)
    address = re.compile(

        r"(\b[가-힣]{2,}(?:특별시|광역시|특별자치시|도)\s*[가-힣]{1,}(?:시|군|구)\s*[가-힣0-9\- ]{2,})|([가-힣]{1,}(?:동|로|길)\s*\d{1,4}(?:-\d{1,4})?)"
    )

    return [
        {"type": "rrn", "regex": rrn, "group": 0},
        {"type": "phone", "regex": phone, "group": 0},
        {"type": "email", "regex": email, "group": 0},
        {"type": "account", "regex": account, "group": 0},
        {"type": "name", "regex": name, "group": 0},
        {"type": "address", "regex": address, "group": 0},
    ]


COMPILED_PATTERNS: List[PiiPattern] = _compile_patterns()


def detect(text: str, types: Optional[List[PiiType]] = None) -> List[PiiMatch]:
    """Detect PII in text.

    Args:
        text: Input text to scan
        types: Optional subset of PII types to detect

    Returns:
        List of matched PII items with type, value, and span (start, end)
    """
    if not text:
        return []

    selected = [p for p in COMPILED_PATTERNS if types is None or p["type"] in types]
    results: List[PiiMatch] = []

    for pattern in selected:
        for m in pattern["regex"].finditer(text):
            value = m.group(pattern["group"]) if pattern["group"] else m.group(0)
            results.append({
                "type": pattern["type"],
                "value": value,
                "span": (m.start(), m.end()),
            })

    # Resolve simple overlaps by preferring more specific types in this order
    priority: Dict[PiiType, int] = {"rrn": 5, "account": 4, "phone": 3, "email": 3, "address": 2, "name": 1}
    results.sort(key=lambda r: (r["span"][0], -r["span"][1]))

    filtered: List[PiiMatch] = []
    for match in results:
        overlapped = False
        for i, kept in enumerate(filtered):
            s1, e1 = match["span"]
            s2, e2 = kept["span"]
            if not (e1 <= s2 or e2 <= s1):
                if priority[match["type"]] > priority[kept["type"]]:
                    filtered[i] = match
                overlapped = True
                break
        if not overlapped:
            filtered.append(match)

    return filtered


def extract(text: str, types: Optional[List[PiiType]] = None) -> Dict[PiiType, List[str]]:
    """Extract detected values grouped by PII type."""
    out: Dict[PiiType, List[str]] = {t: [] for t in ["rrn", "name", "account", "phone", "email", "address"]}
    for m in detect(text, types):
        if m["value"] not in out[m["type"]]:
            out[m["type"]].append(m["value"])
    if types is not None:
        out = {k: v for k, v in out.items() if k in types}
    return out


def _mask_value(value: str, pii_type: PiiType, mask_char: str = "*") -> str:
    if pii_type == "rrn":
        return re.sub(r"(\d{6})-?(\d)", lambda m: f"{m.group(1)}-{mask_char*6}", value)
    if pii_type == "phone":
        return re.sub(r"(\d{2,3})[- ]?(\d{3,4})[- ]?(\d{4})", lambda m: f"{m.group(1)}-{mask_char*len(m.group(2))}-{mask_char*len(m.group(3))}", value)
    if pii_type == "email":
        local, _, domain = value.partition("@")
        if len(local) <= 2:
            return f"{mask_char*len(local)}@{domain}"
        return f"{local[0]}{mask_char*(len(local)-2)}{local[-1]}@{domain}"
    if pii_type == "account":
        digits = re.sub(r"\D", "", value)
        if len(digits) <= 4:
            return mask_char * len(digits)
        masked = f"{mask_char*(len(digits)-4)}{digits[-4:]}"
        # Re-insert hyphens roughly in original positions if present
        if "-" in value:
            parts = [len(p) for p in re.split(r"-", re.sub(r"\D", "-", value)) if p != ""]
            out = []
            idx = 0
            for plen in parts:
                out.append(masked[idx:idx+plen])
                idx += plen
            return "-".join(out)
        return masked
    if pii_type == "name":
        if len(value) <= 1:
            return mask_char
        return value[0] + mask_char * (len(value) - 1)
    if pii_type == "address":
        # Keep initial region token, mask the rest
        tokens = value.split()
        if not tokens:
            return mask_char
        return tokens[0] + " " + mask_char * max(0, len(value) - len(tokens[0]) - 1)
    return mask_char * len(value)


def mask(text: str, types: Optional[List[PiiType]] = None, mask_char: str = "*") -> str:
    """Return text with detected PII masked.

    Masking rules are type-aware to preserve some structure.
    """
    matches = detect(text, types)
    # Replace from end to start to keep spans stable
    masked_text = text
    for m in sorted(matches, key=lambda x: x["span"][0], reverse=True):
        s, e = m["span"]
        masked_text = masked_text[:s] + _mask_value(m["value"], m["type"], mask_char) + masked_text[e:]
    return masked_text


__all__ = [
    "PiiType",
    "PiiMatch",
    "detect",
    "extract",
    "mask",
]


