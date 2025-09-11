def create_molset_response(self, molset, query=None, cache_id=None):
    """
    Return a filtered and paginated subset of a molset, wrapped into
    a response object that is ready to be consumed by the frontend.

    Parameters
    ----------
    molset: list
        The entire list of molecules from a file.
    cache_id: str
        The unique identifier of the working copy of the molset.
    query: dict
        The query parameters from the frontend.
        Eg. { queryStr: "C1=CC=CC=C1", smarts: 1, page: 1, sort: "name" }
    """

    # Parse the query
    query = query if query else {}
    search_str = unquote(query["search"]) if "search" in query else ""
    smarts_mode = query["smarts"] if "smarts" in query else False
    page = int(query["page"]) if "page" in query else 1
    sort = query["sort"] if "sort" in query else None
    page_size = 48  # Hardcoded for now

    # Filter by query
    if search_str:
        results = []
        for mol in molset:
            found = False

            # Substructure search - match against smiles only.
            if smarts_mode:
                if search_str.lower() in mol["identifiers"]["canonical_smiles"].lower():
                    results.append(mol)

            # Regular search - match against all identifiers and properties.
            else:
                for key in mol["identifiers"]:
                    if search_str.lower() in str(mol["identifiers"][key]).lower():
                        results.append(mol)
                        found = True
                        break
                if not found:
                    for key in mol["properties"]:
                        if search_str.lower() in str(mol["properties"][key]).lower():
                            results.append(mol)
                            break

    # No query
    else:
        results = molset

    # Sort
    try:
        # print("INDEX:", molset[0].get("index"))
        # print("SORT:", sort)
        if sort:
            reverse = sort.startswith("-")
            sort_key = sort.lstrip("-")
            results = sorted(
                results,
                key=lambda mol: self._sort_mol(mol, sort_key),
                reverse=reverse,
            )
    except TypeError as err:
        # In the edge case where our dataset mixes string and
        # number values, we want to avoid crashing the app.
        logger.error(f"Error sorting molset: {err}")

    # Store all indices - used by 'select all'
    all_indices = [mol.get("index") for mol in molset]

    # Store matching indices before pagination - used by 'select matching'
    matching_indices = [mol.get("index") for mol in results]

    # Paginate
    total_pages = len(results) // page_size + 1
    page = min(
        page, total_pages
    )  # Make sure that page number is lowered in case of a too high value.
    total = len(molset)
    result_count = len(results)
    skip = 48 * (page - 1)
    results = results[skip : skip + 48]

    return {
        "cacheId": cache_id,  # Used to identify our working copy in next requests
        "mols": results,  # One page of molecules
        "allIndices": all_indices,  # Ids of all molecules
        "matchingIndices": matching_indices,  # Ids of all matching molecules
        "total": total,
        "resultCount": result_count,
        # Query parameters:
        "searchStr": search_str,
        "searchMode": "smarts" if smarts_mode else "text",
        "sort": sort,
        "page": page,
        "pageSize": page_size,
    }
