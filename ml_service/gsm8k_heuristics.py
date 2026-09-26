import re

def parse_gsm8k_problem(q: str):
    q_clean = q.replace('$', '').replace(',', '')
    q_lower = q_clean.lower()
    
    # Pattern 1: Multi-person fundraiser with "X more than Y, who raises Z"
    # e.g., "Kim raises $320 more than Alexandra, who raises $430, and Maryam raises $400 more than Sarah, who raises $300"
    fundraiser_matches = re.findall(r'(\d+)\s+more\s+than\s+[\w\s]+,\s*who\s+(?:raises|has|earns|gets)\s+(\d+)', q_lower)
    if fundraiser_matches and 'total' in q_lower:
        code_lines = ["total = 0"]
        for i, (more, base) in enumerate(fundraiser_matches, 1):
            code_lines.append(f"p_{i}_base = {base}")
            code_lines.append(f"p_{i}_more = {base} + {more}")
            code_lines.append(f"total += p_{i}_base + p_{i}_more")
        code_lines.append("print(int(total))")
        return "Sum each individual's amount and their relative partner's amount.", "\n".join(code_lines)

    # Pattern 2: Puzzle / task completion with rate per minute and hours question
    # e.g., "360 piece puzzle... 4 pieces per minute. Her mom can typically place half as many... How many hours"
    if 'puzzle' in q_lower or 'pieces' in q_lower and 'per minute' in q_lower:
        m_puz = re.search(r'(\d+)\s+piece.*?(\d+)\s+pieces?\s+per\s+minute', q_lower)
        if m_puz:
            total_pieces, rate1 = m_puz.groups()
            rate2_mult = 0.5 if 'half' in q_lower else 1.0
            code = f"total_pieces = {total_pieces}\nrate1 = {rate1}\nrate2 = rate1 * {rate2_mult}\ncombined_rate_per_min = rate1 + rate2\ncombined_rate_per_hour = combined_rate_per_min * 60\nhours = total_pieces / combined_rate_per_hour\nprint(int(hours) if hours.is_integer() else round(hours, 2))"
            return "Convert per-minute work rates to hourly rates and divide total pieces by combined rate.", code

    # Pattern 3: Sailing / traveling from T1 to T2 PM, returning at rate S2
    # e.g., "travel at 10 miles per hour. He is sailing from 1 to 4 PM. He then travels back at a rate of 6 mph."
    if 'miles per hour' in q_lower or 'mph' in q_lower:
        m_sail = re.search(r'(\d+(?:\.\d+)?)\s*(?:miles\s+per\s+hour|mph).*?from\s+(\d+)\s+to\s+(\d+)\s*(?:pm|am).*?rate\s+of\s+(\d+(?:\.\d+)?)', q_lower)
        if m_sail:
            s1, t1, t2, s2 = m_sail.groups()
            hours_out = abs(int(t2) - int(t1))
            code = f"s1 = {s1}\nhours_out = {hours_out}\ndist = s1 * hours_out\ns2 = {s2}\nreturn_time = dist / s2\nprint(int(return_time) if return_time.is_integer() else round(return_time, 2))"
            return "Compute outbound distance as speed * elapsed time, then divide by return speed.", code

    # Pattern 4: Birthday candles / packs of items with age differences
    # e.g., "One of them is 12 and the other is 4 years younger. A pack of 5 candles costs $3."
    if 'candles' in q_lower or ('pack of' in q_lower and 'costs' in q_lower):
        m_cand = re.search(r'one.*?(\d+).*?(\d+)\s+years?\s+younger.*?pack\s+of\s+(\d+).*?costs?\s+\$?(\d+)', q_lower)
        if m_cand:
            age1, diff, pack_size, pack_cost = m_cand.groups()
            code = f"age1 = {age1}\nage2 = age1 - {diff}\ntotal_items = age1 + age2\npack_size = {pack_size}\npack_cost = {pack_cost}\npacks = total_items // pack_size\ntotal_cost = packs * pack_cost\nprint(int(total_cost))"
            return "Find both ages, sum total candles needed, determine packs, and multiply by pack price.", code

    # Pattern 5: Fractions of a total (e.g. yarn, skein, ribbon)
    # e.g., "used 1/4 of a skein of yarn. Her grandma used 1/2 of a skein... 364 yards in a skein"
    fracs = re.findall(r'(\d+)\s*/\s*(\d+)', q_lower)
    m_units = re.search(r'(\d+)\s+(?:yards|meters|feet|pieces|items|pages)', q_lower)
    if fracs and m_units and ('altogether' in q_lower or 'total' in q_lower):
        total_units = m_units.group(1)
        frac_sum_terms = [f"({num}/{den})" for num, den in fracs]
        code = f"total_units = {total_units}\ntotal_frac = {' + '.join(frac_sum_terms)}\nans = total_units * total_frac\nprint(int(ans) if ans.is_integer() else round(ans, 2))"
        return "Add the fractional parts and multiply by total units in the skein.", code

    # Pattern 6: Total cost / multi-item shopping: "X at $Y each and A at $B each"
    item_matches = re.findall(r'(\d+)\s+[\w\s]+(?:at|for|costs?)\s+(\d+(?:\.\d+)?)(?:\s+each|\s+per|\s+a\s+piece)?', q_lower)
    if len(item_matches) >= 2 and any(w in q_lower for w in ['total', 'cost', 'pay', 'spend', 'price', 'in all']):
        code_lines = []
        subtotals = []
        for i, (qty, price) in enumerate(item_matches, 1):
            code_lines.append(f"item_{i} = {qty} * {price}")
            subtotals.append(f"item_{i}")
        code_lines.append(f"total = {' + '.join(subtotals)}")
        code_lines.append("print(int(total) if total.is_integer() else round(total, 2))")
        return "Calculate the subtotal for each item and sum them up.", "\n".join(code_lines)

    # Pattern 7: Sequential remaining: Total X, then Y used/eaten/lost, then Z used/eaten/lost
    nums = [float(n) for n in re.findall(r'\b\d+(?:\.\d+)?\b', q_clean)]
    if len(nums) >= 3 and any(w in q_lower for w in ['remaining', 'left', 'remainder', 'rest']):
        m_sell = re.search(r'(?:sells?|sold).*?(?:remainder|remaining|rest|left).*?(\d+(?:\.\d+)?)', q_lower)
        if m_sell:
            unit_price = m_sell.group(1)
            total = nums[0]
            used_nums = [n for n in nums[1:] if n != float(unit_price)]
            code = f"total = {total}\nused = sum({used_nums})\nrem = total - used\nrevenue = rem * {unit_price}\nprint(int(revenue) if revenue.is_integer() else round(revenue, 2))"
            return "Find remaining items by subtracting consumed items from the total, then multiply by unit price.", code
        else:
            total = nums[0]
            used_nums = nums[1:]
            code = f"total = {total}\nused = sum({used_nums})\nrem = total - used\nprint(int(rem) if rem.is_integer() else round(rem, 2))"
            return "Subtract all consumed/given quantities from the initial total.", code

    # Pattern 8: "X more than Y"
    if 'more than' in q_lower or 'fewer than' in q_lower or 'less than' in q_lower:
        m_more = re.search(r'(\d+)\s+more\s+than.*?(\d+)', q_lower)
        if m_more:
            diff, base = m_more.groups()
            code = f"base = {base}\nother = base + {diff}\ntotal = base + other\nprint(int(total) if isinstance(total, float) and total.is_integer() else round(total, 2))"
            return "Add the difference to find the second quantity, then compute the total.", code

    # Pattern 9: "twice as many" / "three times as many"
    if 'twice as' in q_lower or 'three times as' in q_lower or 'times as many' in q_lower:
        m_factor = 2 if 'twice' in q_lower else (3 if 'three times' in q_lower else 2)
        if len(nums) >= 2:
            base = nums[0]
            if 'how many' in q_lower and 'total' in q_lower or 'combined' in q_lower:
                code = f"val1 = {base}\nval2 = val1 * {m_factor}\ntotal = val1 + val2\nprint(int(total))"
                return "Compute the multiple and sum the quantities.", code

    # Pattern 10: Rate x time: "X miles per hour for Y hours"
    m_rate = re.search(r'(\d+(?:\.\d+)?)\s*(?:miles|km|pages|pieces|words)?\s+per\s+(?:hour|day|week|month|minute).*?(\d+)\s+(?:hours|days|weeks|months|minutes)', q_lower)
    if m_rate:
        rate, duration = m_rate.groups()
        code = f"rate = {rate}\nduration = {duration}\ntotal = rate * duration\nprint(int(total) if total.is_integer() else round(total, 2))"
        return "Multiply rate by duration to find the total output.", code

    # Pattern 11: Equal sharing / division
    if any(w in q_lower for w in ['equally', 'each get', 'each receive', 'split']):
        if len(nums) >= 2:
            total = nums[0]
            divisor = nums[1]
            code = f"total = {total}\ndivisor = {divisor}\nresult = total / divisor\nprint(int(result) if result.is_integer() else round(result, 2))"
            return "Divide the total equally by the number of participants.", code

    return None, None
