#!/usr/bin/env bash
# AI-Harness Autocomplete Script for Bash/Zsh

_aih_completion() {
    local cur prev commands modes targets
    COMPREPLY=()
    cur="${COMP_WORDS[COMP_CWORD]}"
    prev="${COMP_WORDS[COMP_CWORD-1]}"

    commands="do ask prompt route run new-run latest-run doctor manifest validate release health install-shell list show compile"
    modes="auto implementation debug review research architecture security extraction eval"
    targets="auto codex claude generic"

    case "${prev}" in
        --mode)
            COMPREPLY=( $(compgen -W "${modes}" -- ${cur}) )
            return 0
            ;;
        --target)
            COMPREPLY=( $(compgen -W "${targets}" -- ${cur}) )
            return 0
            ;;
    esac

    if [[ ${COMP_CWORD} -eq 1 ]]; then
        COMPREPLY=( $(compgen -W "${commands}" -- ${cur}) )
        return 0
    fi
}

complete -F _aih_completion aih
